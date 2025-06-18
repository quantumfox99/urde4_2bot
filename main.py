import asyncio
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler,
    ContextTypes
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import pytz
import random

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENWEATHER_TOKEN = os.getenv("OPENWEATHER_TOKEN")

USERS = [
    {"chat_id": 123456789, "name": "Имя", "city": "Warsaw", "timezone": "Europe/Warsaw", "role": "admin"},
    {"chat_id": 987654321, "name": "Женя", "city": "Warsaw", "timezone": "Europe/Warsaw", "role": "user"},
    {"chat_id": 111222333, "name": "Рома", "city": "Rivne", "timezone": "Europe/Kyiv", "role": "user"},
    {"chat_id": 444555666, "name": "Витек", "city": "Kelowna", "timezone": "America/Vancouver", "role": "user"},
    {"chat_id": 777888999, "name": "Никита", "city": "Warsaw", "timezone": "Europe/Warsaw", "role": "user"},
]

PREDICTIONS = [
    "Сегодня тебе улыбнётся удача!",
    "Будь осторожен в пути.",
    "Жди хорошие новости вечером.",
    "Идеальный день, чтобы начать что-то новое!"
]

def get_weather(city: str) -> str:
    # Здесь ты можешь подключить реальный API OpenWeatherMap
    return f"Погода в {city}: +20°C, облачно"

def main_admin_keyboard():
    keyboard = [
        [KeyboardButton("🔍 Поиск запчасти"), KeyboardButton("🚗 Выбор модели")],
        [KeyboardButton("🛒 Корзина"), KeyboardButton("🔁 Сброс поиска")],
        [KeyboardButton("🔄 Синхронизировать"), KeyboardButton("📚 Логи запросов")],
        [KeyboardButton("👥 Список пользователей")],
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие",
        is_persistent=True,
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = next((u for u in USERS if u["chat_id"] == user_id), None)

    if user:
        text = f"Привет, {user['name']}!"
        reply_markup = main_admin_keyboard() if user["role"] == "admin" else None
        await update.message.reply_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text("Вы не зарегистрированы.")

async def send_weather(application):
    now_utc = datetime.now(pytz.utc)
    for user in USERS:
        try:
            if not user.get("chat_id"):
                continue
            local_tz = pytz.timezone(user["timezone"])
            local_now = now_utc.astimezone(local_tz)
            if local_now.hour != 7 or local_now.minute > 10:
                continue
            message = f"{get_weather(user['city'])}\nПредсказание: {random.choice(PREDICTIONS)}"
            await application.bot.send_message(chat_id=user["chat_id"], text=message)
        except Exception as e:
            print(f"Ошибка для {user['name']}: {e}")

async def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: asyncio.create_task(send_weather(application)), "interval", minutes=10)
    scheduler.start()

    print("Бот запущен.")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
