import os
import asyncio
import random
import pytz
import requests
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENWEATHER_TOKEN = os.getenv("OPENWEATHER_TOKEN")

# Список пользователей
USERS = [
    {"chat_id": 123456789, "name": "Женя", "city": "Warsaw", "timezone": "Europe/Warsaw"},
    {"chat_id": 987654321, "name": "Никита", "city": "Warsaw", "timezone": "Europe/Warsaw"},
    {"chat_id": 555555555, "name": "Рома", "city": "Rivne", "timezone": "Europe/Kyiv"},
    {"chat_id": 444444444, "name": "Витек", "city": "Kelowna", "timezone": "America/Vancouver"},
]

PREDICTIONS = [
    "Сегодня тебе улыбнётся удача!",
    "Будь осторожен в пути.",
    "Жди хорошие новости вечером.",
    "Идеальный день, чтобы начать что-то новое.",
    "Не забывай пить воду!",
    "Возможно, сегодня ты получишь неожиданный комплимент.",
    "Старый друг может напомнить о себе.",
    "Один шаг — уже движение вперёд.",
    "Не все чудеса громкие. Присмотрись.",
    "Сегодня день для добрых поступков."
    # Добавим позже ещё 200+
]

def get_weather(city: str) -> str:
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_TOKEN}&units=metric&lang=ru"
        response = requests.get(url)
        data = response.json()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"].capitalize()
        return f"🌤️ Погода в {city}: {temp}°C, {desc}"
    except Exception as e:
        return f"Не удалось получить погоду для {city}: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я отправляю погоду и предсказания каждый день в 7:00.")

async def send_weather(app):
    now = datetime.now(pytz.utc)
    for user in USERS:
        tz = pytz.timezone(user["timezone"])
        local_now = now.astimezone(tz)
        if local_now.hour == 7 and local_now.minute < 10:
            weather = get_weather(user["city"])
            prediction = random.choice(PREDICTIONS)
            text = f"{weather}\n\n🔮 Предсказание на день:\n{prediction}"
            try:
                await app.bot.send_message(chat_id=user["chat_id"], text=text)
            except Exception as e:
                print(f"Ошибка для {user['name']}: {e}")

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: asyncio.create_task(send_weather(app)), "interval", minutes=10)
    scheduler.start()

    print("Бот запущен")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
