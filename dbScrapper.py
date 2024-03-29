import psycopg2
import json
import telegram
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler
import time
import os
import sys
import asyncio
import environ
from pathlib import Path
from pytz import timezone

BASE_DIR = Path(__file__).resolve().parent
env = environ.Env(
    TIMEOUT=(int, 60),
    CHAT_ID=(int, 0)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

TOKEN = env('TOKEN_BOT')  # не изменный, токен бота
CHAT_ID = env('CHAT_ID')  # чат айди - стоит заглушка


def connect_to_database():
    try:
        conn = psycopg2.connect(
            dbname=env('DB_NAME'),
            user=env('DB_USER'),
            password=env('DB_PASSWORD'),
            host=env('DB_HOST'),
            port=env('DB_PORT'),
        )
        print("Connected to the database")
        return conn
    except psycopg2.Error as e:
        print(f"Unable to connect to the database: {e}")
        return None


async def send_message(token, chat_id, message, photos=None):
    bot = Bot(token=token)

    print('----------SENDING MESSSAGE-------------')
    print(token, chat_id, message, photos, sep='\n')
    print('---------------------------------------')

    if photos is not None:
        await bot.send_media_group(chat_id=chat_id, media=photos, caption=message)
    else:
        await bot.send_message(chat_id=chat_id, text=message)


async def check_database_changes(conn, previous_data):
    cur = conn.cursor()
    cur.execute("SELECT id, review_text, pub_date FROM api_review;")
    rows = cur.fetchall()

    new_data = set(row[0] for row in rows)
    differences = new_data - previous_data

    for row in rows:
        id = row[0]
        if id in differences:
            review_text, pub_date = row[1], row[2]
            local_pub_date = pub_date.astimezone(timezone('Asia/Yekaterinburg'))
            message = f"Обращение:\n{review_text}\nДата публикации: {local_pub_date.strftime('%H:%M %d/%m/%Y')}"
            cur.execute(
                "SELECT image FROM api_image WHERE review_id=%s", (id,))

            photo_paths = [os.path.join('media', photo[0])
                           for photo in cur.fetchall()]

            media_group = [telegram.InputMediaPhoto(
                open(image_path, 'rb')) for image_path in photo_paths]

            if len(media_group) > 0:
                await send_message(TOKEN, CHAT_ID, message, media_group)
            else:
                await send_message(TOKEN, CHAT_ID, message)

    return new_data


async def save_previous_data(previous_data, filename='previous_data.json'):
    with open(filename, 'w') as f:
        json.dump(list(previous_data), f)


async def load_previous_data(filename='previous_data.json'):
    try:
        with open(filename, 'r') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()


async def main():
    conn = connect_to_database()
    if conn is None:
        print("Unable to connect to the database")
        return

    previous_data = await load_previous_data()

    while True:
        previous_data = await check_database_changes(conn, previous_data)
        await save_previous_data(previous_data)
        await asyncio.sleep(env('TIMEOUT'))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(1)
