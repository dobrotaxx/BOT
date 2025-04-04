import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
import google.generativeai as genai
from pprint import pprint

print("=== ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ===")
pprint({k: v for k, v in os.environ.items() if 'TOKEN' in k or 'API' in k or 'KEY' in k})

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TELEGRAM_TOKEN:
    print("❌ ОШИБКА: TELEGRAM_TOKEN не найден!")
    print("Добавьте его в Railway → Variables")
    exit(1)

if not GEMINI_API_KEY:
    print("❌ ОШИБКА: GEMINI_API_KEY не найден!")
    exit(1)

print("✅ Все переменные найдены. Запуск бота...")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

async def handle_message(update: Update, context):
    try:
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {str(e)}")

app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🟢 Бот запущен и ожидает сообщений...")
app.run_polling()