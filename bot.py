import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# API kalitlar
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini sozlash
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Har foydalanuvchi uchun suhbat tarixi
chat_sessions = {}

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"Assalomu alaykum, {user_name}! 👋\n\n"
        f"Men AI yordamchiman. Har qanday savolingizni bering!\n\n"
        f"📌 Komandalar:\n"
        f"/start - Boshlash\n"
        f"/help - Yordam\n"
        f"/clear - Suhbatni tozalash"
    )

# /help komandasi
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Men AI yordamchiman!\n\n"
        "✅ Nima qila olaman:\n"
        "- Savollarga javob berish\n"
        "- Matn yozish va tarjima qilish\n"
        "- Kod yozish\n"
        "- Maslahat berish\n"
        "- Suhbat qilish\n\n"
        "💬 Shunchaki xabar yozing!"
    )

# /clear komandasi
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in chat_sessions:
        del chat_sessions[user_id]
    await update.message.reply_text("✅ Suhbat tarixi tozalandi!")

# Xabarlarni qayta ishlash
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    # Yozmoqda... ko'rsatish
    await update.message.chat.send_action("typing")

    try:
        # Yangi suhbat yoki mavjud suhbatni davom ettirish
        if user_id not in chat_sessions:
            chat_sessions[user_id] = model.start_chat(history=[])

        chat = chat_sessions[user_id]
        response = chat.send_message(user_message)
        reply = response.text

        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"Xato: {e}")
        await update.message.reply_text(
            "❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring yoki /clear bosing."
        )

# Asosiy funksiya
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Komandalar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear))

    # Xabarlar
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot ishga tushdi! 🚀")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
