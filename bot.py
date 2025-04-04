import os
import time
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from collections import defaultdict

# --- Безопасная загрузка ключей ---
TELEGRAM_TOKEN = os.getenv("7671191191:AAGy1Bja9D4DPPXdZjpJSB5AjEnptibkBqg")  # Берем из переменных среды
GEMINI_API_KEY = os.getenv("AIzaSyCPs9Wa7quNIYXgFknNT219AC5FWNDmFW4")

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("API keys not set in environment variables!")

# --- Инициализация Gemini ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# --- Инициализация Telegram ---
app = Application.builder().token(TELEGRAM_TOKEN).build()

# --- Защита от перегрузки ---
user_last_request = defaultdict(float)  # {user_id: last_request_time}


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_time = time.time()

    # Проверяем интервал между запросами для КОНКРЕТНОГО пользователя
    if current_time - user_last_request[user_id] < 2:
        await update.message.reply_text("⚠️ Подождите 2 секунды между запросами")
        return

    user_last_request[user_id] = current_time

    try:
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)

    except genai.types.StopCandidateException:
        await update.message.reply_text("🚫 Лимит запросов. Попробуйте позже.")
    except Exception as e:
        await update.message.reply_text("⚠️ Ошибка обработки запроса")
        print(f"Error: {e}")  # Логируем для себя


app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    print("🟢 Бот запущен с защитой от перегрузки")
    app.run_polling()