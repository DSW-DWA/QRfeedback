# QRfeedback
Сервис позволяющий по собирать обратную  связь с помощью QR-кода

Установка окружения на Windows
```
py -m venv venv
venv\Script\activate.bat
pip install -r requirements.txt
```

## Локальный запуск проекта
1. Создать пользователя и базу данных в PostgreSQL (если не создано заранее):
```
createuser qrfeedbackuser -P
createdb -O qrfeedbackuser qrfeedackdb
```
2. Создать .env файл в корне джанго проекта (в папке с manage.py). Пример файла с необходимыми полями:
```
DEBUG=True
HTTPS=False
DB_NAME=qrfeedbackdb
DB_USER=qrfeedbackuser
DB_PASSWORD=qrfeedbackpassword
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=
CHAT_ID=
TOKEN_BOT=
TIMEOUT=
```
3. Провести и применить миграции:
```
python manage.py makemigrations
python manage.py migrate
```
4. Создать суперюзера для упрощенного управления моделями через панель админа (опционально):
```
python manage.py createsuperuser
```
5. Запустить сервер:
```
python manage.py runserver
```

## Документация
- [Спецификация API](https://valley-barge-996.notion.site/QRfeedback-API-58136eee7c084d1784763863757e88b5)
- [Схема базы данных](https://dbdiagram.io/d/QRFeedback-65e3c4f0cd45b569fb5fbb88)
