import psycopg2
import json
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler
import time
import os
import asyncio
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

token="7058906839:AAHvC7xiBEEf2oscvEhzGAD09AYdq6F1CSg" #не изменный, токен бота
chat_id=647621082 # чат айди - стоит заглушка

# Подключение к базе данных PostgreSQL
def connect_to_database():
    try:
        conn = psycopg2.connect(
            dbname=env('DB_NAME'), #возможно другое название БД
            user=env('DB_USER'),# возможно другое имя пользователя
            password=env('DB_PASSWORD'), # возможен другой пароль
            port=env('DB_PORT')     # возможен другой порт
        )
        print("Connected to the database")
        return conn
    except psycopg2.Error as e:
        print(f"Unable to connect to the database: {e}")
        return None

async def send_message(token, chat_id, message, photo=None):
    bot = Bot(token=token)
    if photo:
        await bot.send_photo(chat_id=chat_id, photo=photo, caption=message)
    else:
        await bot.send_message(chat_id=chat_id, text=message)

async def check_database_changes(conn, previous_data):
    cur = conn.cursor()
    cur.execute("SELECT id, review_text, pub_date, image FROM api_review;")
    rows = cur.fetchall()

    new_data = set(row[0] for row in rows)
    differences = new_data - previous_data

    for row in rows:
        if row[0] in differences:
            message = f"Отзыв:\n{row[1]}\nДата публикации: {row[2]}"
            if row[3]:
                photos = row[3]
                for photo in photos:
                    await send_message(token, chat_id, message, photo)
            else:
                await send_message(token, chat_id, message)

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
        await asyncio.sleep(60)  # ожидание 60 секунд перед следующей проверкой, можно поменять значение, чтобы чаще проверялось

if __name__ == "__main__":
    asyncio.run(main())