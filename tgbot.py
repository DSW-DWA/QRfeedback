import asyncio
import csv
import logging

import numpy as np
from keras.models import load_model
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from tensorflow.keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import pandas as pd
from telegram.update import Update
from telegram.ext import CallbackContext, Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

namesOfClasses = ["Часы работы","код клуба","Заморозка карты","не посещал по состояню здоровья","куда отправлять справку-больничный"
                  ,"диагностика","бесплатная тренировка","расторжение","гостевой входит ли","персональные тренеры","справка для посещения бассейна"
                  ,"разовый визит","хочу пригласить друга","в какое время меньше всего человек","аренда персональных шкафчиков","правила посещения ТЗ"
                  ,"перефоормление карты","не получается записаться на тренировки","приложение не работает","не могу заморозить карту","хочу массаж, есть ли солярий"
                  ,"нужна справка для налогового вычета", "хочу карту маме папе","есть ли только бассейн","есть ли подарочные сертификаты","у меня уже есть карта"
                  ,"кто мой менеджер","почему меня не предупредили о отмене тренировки","со мной не связались","есть ли бонусы за привод друга",
                  "куда можно оставить отзыв","сколько сейчас человек в бассейне"]

model = load_model('question_classification_model.h5')

max_words = 1000
max_len = 50

data = pd.read_csv('dataset.csv', names=['answer', 'question'], delimiter='`')
tokenizer = Tokenizer(num_words=max_words, filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n', lower=True)
tokenizer.fit_on_texts(data['question'])

def start(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я бот, который может классифицировать вопросы. Задайте мне вопрос, и я постараюсь отнести его к одному из классов.")

def handle_callback_query(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data

    if data == "yes":
        pass

    elif data == "no":
        question_text = query.message.text

        with open("new_info.csv", "a", newline="",encoding="UTF-8") as csvfile:
            writer = csv.writer(csvfile, delimiter="`")
            writer.writerow([question_text])

    query.message.delete()


def handle_text_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text

    processed_text = tokenizer.texts_to_sequences([text])
    processed_text = pad_sequences(processed_text, maxlen=max_len)

    processed_text = np.squeeze(processed_text)

    predicted_class = model.predict(np.array([processed_text]))
    predicted_class = np.argmax(predicted_class) + 1

    keyboard = [
        [
            InlineKeyboardButton("Да", callback_data="yes"),
            InlineKeyboardButton("Нет", callback_data="no"),
        ]
    ]

    markup = InlineKeyboardMarkup(keyboard)
    print(text)
    print(f"Предсказанный класс: {predicted_class},{namesOfClasses[predicted_class - 1]}")
    print("-------------------------------")
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"{predicted_class}`{namesOfClasses[predicted_class - 1]}`{text}",
        reply_markup=markup,
    )
#text=f"Предсказанный класс: {predicted_class},{namesOfClasses[predicted_class - 1]}` текст вопроса: {text}",



async def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


    import os
    TOKEN = "7058906839:AAHvC7xiBEEf2oscvEhzGAD09AYdq6F1CSg"

    updater = Updater(token=TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_text_message))
    dispatcher.add_handler(CallbackQueryHandler(handle_callback_query))
    updater.start_polling()
    updater.idle()


    #while True:
     #   print("xcczczc")
      #  updater.update_queue.put_nowait(updater.bot.get_updates())
       # updates = updater.bot.get_updates()
        #print(f"Received {len(updates)} updates")
        #for update in updates:
         #   print(update)
        #updater.update_queue.put_nowait(updates)
        #await asyncio.sleep(15)
if __name__ == "__main__":
    print("запускаем мейн")
    asyncio.run(main())