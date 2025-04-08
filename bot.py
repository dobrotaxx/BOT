import os
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
import google.generativeai as genai
from pprint import pprint
from datetime import datetime, timedelta

# --- Конфигурация ---
print("=== ДИАГНОСТИКА ===")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")  # Новый ключ для погоды

# Проверка переменных окружения
if not all([TELEGRAM_TOKEN, GEMINI_API_KEY, WEATHER_API_KEY]):
    missing = []
    if not TELEGRAM_TOKEN: missing.append("TELEGRAM_TOKEN")
    if not GEMINI_API_KEY: missing.append("GEMINI_API_KEY")
    if not WEATHER_API_KEY: missing.append("WEATHER_API_KEY")
    print(f"❌ ОШИБКА: Отсутствуют переменные - {', '.join(missing)}")
    exit(1)

print("✅ Все переменные найдены. Запуск бота...")

# --- Инициализация Gemini ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# --- Система ограничения запросов ---
user_requests = {}


def check_rate_limit(user_id: int) -> bool:
    """Проверяет, не превышен ли лимит запросов (1 в минуту)"""
    now = datetime.now()
    if user_id in user_requests:
        last_request = user_requests[user_id]
        if now - last_request < timedelta(minutes=1):
            return False
    user_requests[user_id] = now
    return True


# --- Обработчики сообщений ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start с клавиатурой"""
    keyboard = [
        [KeyboardButton("🌤️ Узнать погоду")],
        [KeyboardButton("💬 Задать вопрос")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Выберите действие:",
        reply_markup=reply_markup
    )


async def handle_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик запросов погоды"""
    user_id = update.message.from_user.id

    if not check_rate_limit(user_id):
        await update.message.reply_text("⚠️ Слишком частые запросы. Попробуйте через минуту.")
        return

    try:
        city = "Екатеринбург"  # Можно сделать выбор города
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        response = requests.get(url).json()

        if response['cod'] != 200:
            raise Exception(response['message'])

        temp = response['main']['temp']
        description = response['weather'][0]['description']
        await update.message.reply_text(
            f"🌤 Погода в {city}:\n"
            f"• Температура: {temp}°C\n"
            f"• Описание: {description.capitalize()}"
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка при запросе погоды: {str(e)}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений (для Gemini)"""
    if update.message.text == "🌤️ Узнать погоду":
        await handle_weather(update, context)
        return

    try:
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {str(e)}")


# --- Запуск бота ---
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🟢 Бот запущен и ожидает сообщений...")
    app.run_polling()


if __name__ == "__main__":
    main()