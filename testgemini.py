import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Настройка Gemini
GEMINI_API_KEY = "AIzaSyCTnUIc9acUIWlTD_IAW3w8zZxyBIxj6pE"
genai.configure(
    api_key=GEMINI_API_KEY,
    client_options={"api_endpoint": "https://generativelanguage.googleapis.com/v1"}
)

# Используем доступную модель из вашего списка
MODEL_NAME = "models/gemini-1.5-pro-latest"  # Или models/gemini-1.5-flash-latest для более быстрого варианта
model = genai.GenerativeModel(MODEL_NAME)

# Настройка Telegram
TELEGRAM_TOKEN = "7671191191:AAGYZJdxSB7q4KTQNcDL7fOoCrqKJuZej9Y"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {str(e)}")

app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()