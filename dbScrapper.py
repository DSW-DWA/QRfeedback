#!/usr/bin/env python

import psycopg2
import json
import telegram
import tempfile
from telegram.ext import Application, CommandHandler
import os
import sys
import environ
from pathlib import Path
from pytz import timezone

BASE_DIR = Path(__file__).resolve().parent
env = environ.Env(
    TIMEOUT=(int, 10),
    DB_PORT=(str, "5432"),
    MEDIA_ROOT=(str, "data"),
    HOSTNAME=(str, "127.0.0.1")
)

env.read_env(BASE_DIR / env.str('ENV_PATH', '.env'))

TOKEN = env("TOKEN_BOT")
TGBOT = telegram.Bot(token=TOKEN)


def connect_to_database():
    try:
        conn = psycopg2.connect(
            dbname=env("DB_NAME"),
            user=env("DB_USER"),
            password=env("DB_PASSWORD"),
            host=env("DB_HOST"),
            # host="localhost",
            port=env("DB_PORT"),
        )
        return conn
    except psycopg2.Error as e:
        return None


async def send_message(bot, chat_id, message, thread_id=None, photos=None):

    print("----------SENDING MESSSAGE-------------")
    print("CHAT_ID:", chat_id)
    print("THREAD_ID:", thread_id)
    print("MESSAGE:", message)
    print("PHOTOS:", photos)
    print("---------------------------------------")

    try:
        if photos is not None:
            await bot.send_media_group(chat_id=chat_id, message_thread_id=thread_id, media=photos, caption=message)
        else:
            await bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text=message)
    except Exception as e:
        print(e)


async def check_database_changes(bot, previous_data):
    conn = connect_to_database()
    if conn is None:
        print("Unable to connect to the database")
        sys.exit(1)

    cur = conn.cursor()
    cur.execute(
        "SELECT id, review_text, pub_date, address, tg_session_id, tg_thread_id FROM api_review;"
    )
    rows = cur.fetchall()

    new_data = set(row[0] for row in rows)
    differences = new_data - previous_data

    for row in rows:
        id = row[0]
        if id in differences:
            review_text, pub_date, address, tg_session_id, tg_thread_id = row[1:]

            local_pub_date = pub_date.astimezone(
                timezone("Asia/Yekaterinburg"))

            message = f"\
Адрес:\n{address}\n\n\
Обращение:\n{review_text}\n\n\
Дата публикации: {local_pub_date.strftime('%H:%M %d/%m/%Y')}"

            cur.execute(
                "SELECT image FROM api_image WHERE review_id=%s", (id,))

            photo_paths = [os.path.join(env("MEDIA_ROOT"), "media", photo[0])
                           for photo in cur.fetchall()]

            media_group = [
                telegram.InputMediaPhoto(open(image_path, "rb"))
                for image_path in photo_paths
            ]

            if len(media_group) > 0:
                await send_message(bot, tg_session_id, message, tg_thread_id, media_group)
            else:
                await send_message(bot, tg_session_id, message, tg_thread_id)

    cur.close()
    conn.close()
    return new_data


async def save_previous_data(previous_data, filename="previous_data.json"):
    with open(filename, "w") as f:
        json.dump(list(previous_data), f)


async def load_previous_data(filename="previous_data.json"):
    try:
        with open(filename, "r") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()


async def set_bot_commands(context):
    reportCmd = telegram.BotCommand(
        "report", "Скачать отчет в формате таблицы для всех обращений")

    await context.bot.set_my_commands([reportCmd])


async def poll_db(context):
    previous_data = await load_previous_data()
    previous_data = await check_database_changes(context.bot, previous_data)
    await save_previous_data(previous_data)


class ReportReviewEntry:
    def __init__(self, address, review, pub_date, image):
        self.address = address
        self.review = review
        self.pub_date = pub_date.astimezone(
            timezone("Asia/Yekaterinburg")).strftime('%H:%M %d/%m/%Y')
        self.images = [image] if image is not None else []

    def __str__(self):
        images_str = ",".join(self.images)
        return f'(Address: {self.address}, Review: {self.review}, Local date: {self.pub_date}, Images: {images_str})'

    def format_images(self):
        return '\n'.join(self.images)


def print_dict(d):
    for k, v in d.items():
        print(k, v)


def fetch_report_data(chat_id):
    conn = connect_to_database()
    if conn is None:
        print("Unable to connect to the database")
        sys.exit(1)

    cur = conn.cursor()
    cur.execute(
        "select R.id, address, review_text, pub_date, image from api_review AS R LEFT JOIN api_image AS I on R.id=I.review_id WHERE tg_session_id=%s;", (str(chat_id),))
    rows = cur.fetchall()
    reviews = {}
    for row in rows:
        id, address, review, pub_date, image_url = row
        if id in reviews:
            reviews[id].images.append(image_url)
        else:
            reviews[id] = ReportReviewEntry(
                address, review, pub_date, image_url)
    cur.close()
    conn.close()
    return reviews


def create_report(chat_id):
    reviews = fetch_report_data(chat_id)
    # with open('test.csv', 'w', newline='') as f:
    # with tempfile.NamedTemporaryFile('w+t') as f:
    from openpyxl import Workbook

    workbook = Workbook()
    worksheet = workbook.active

    import io
    f = io.StringIO()
    fieldnames = ['Адрес', 'Текст обращения',
                  'Дата и время', 'Ссылки на изображения']
    worksheet.append(fieldnames)

    # csv_writer = csv.DictWriter(f, dialect='excel', fieldnames=fieldnames)
    # csv_writer.writeheader()

    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        tmp_name = f.name
        for r in reviews.values():
            imgs = []
            for img in r.images:
                imgs.append(os.path.join(env('HOSTNAME'), 'media', img))

            data = [r.address, r.review, r.pub_date, '\n'.join(imgs)]
            worksheet.append(data)

        workbook.save(tmp_name)

    return tmp_name


async def reportCmdHandler(update, context):
    chat_id = update.message.chat_id
    thread_id = update.message.message_thread_id
    report = create_report(chat_id)

    await context.bot.send_document(chat_id=chat_id, message_thread_id=thread_id, document=open(report, 'rb'), filename='report.xlsx')


def main():
    conn = connect_to_database()
    if conn is not None:
        print("Database connection has been established")
    else:
        print("Unable to connect to the database")
        sys.exit(1)
    conn.close()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("report", reportCmdHandler))

    job_queue = app.job_queue
    job_queue.run_once(set_bot_commands, 0)
    job_queue.run_repeating(poll_db, env("TIMEOUT"))

    app.run_polling()


if __name__ == "__main__":
    main()
