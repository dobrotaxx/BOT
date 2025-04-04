import os
import time
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from collections import defaultdict

# --- Проверка переменных среды ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("❌ Ошибка: TELEGRAM_TOKEN или GEMINI_API_KEY не найдены. Проверьте переменные в Railway!")

# --- Инициализация Gemini ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro-latest')  # Или 'gemini-1.5-flash-latest' для более быстрой работы

# --- Инициализация Telegram бота ---
app = Application.builder().token(TELEGRAM_TOKEN).build()

# --- Защита от перегрузки ---
user_last_request = defaultdict(float)  # {user_id: timestamp}


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        current_time = time.time()

        # Проверяем интервал между запросами (не чаще 1 запроса в 2 секунды)
        if current_time - user_last_request[user_id] < 2:
            await update.message.reply_text("⚠️ Подождите 2 секунды между запросами")
            return

        user_last_request[user_id] = current_time

        # Получаем ответ от Gemini
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)

    except genai.types.StopCandidateException:
        await update.message.reply_text("🚫 Превышен лимит запросов к Gemini. Попробуйте через минуту.")
    except Exception as e:
        await update.message.reply_text("⚠️ Произошла ошибка. Мы уже работаем над исправлением!")
        print(f"Ошибка в handle_message: {str(e)}")  # Логируем для диагностики


# --- Регистрация обработчиков ---
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Запуск бота ---
if __name__ == "__main__":
    print("🟢 Бот успешно запущен!")
    app.run_polling()