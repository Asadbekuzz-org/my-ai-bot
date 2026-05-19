import os
import logging
import telebot
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

chat_histories = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    bot.reply_to(message,
        f"Assalomu alaykum, {user_name}! 👋\n\n"
        f"Men AI yordamchiman. Har qanday savolingizni bering!\n\n"
        f"📌 Komandalar:\n"
        f"/start - Boshlash\n"
        f"/help - Yordam\n"
        f"/clear - Suhbatni tozalash"
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message,
        "🤖 Men AI yordamchiman!\n\n"
        "✅ Nima qila olaman:\n"
        "- Savollarga javob berish\n"
        "- Matn yozish va tarjima qilish\n"
        "- Kod yozish\n"
        "- Maslahat berish\n"
        "- Suhbat qilish\n\n"
        "💬 Shunchaki xabar yozing!"
    )

@bot.message_handler(commands=['clear'])
def clear(message):
    user_id = message.from_user.id
    if user_id in chat_histories:
        del chat_histories[user_id]
    bot.reply_to(message, "✅ Suhbat tarixi tozalandi!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user_text = message.text

    bot.send_chat_action(message.chat.id, 'typing')

    try:
        if user_id not in chat_histories:
            chat_histories[user_id] = []

        chat_histories[user_id].append({"role": "user", "parts": [user_text]})
        response = model.generate_content(chat_histories[user_id])
        reply = response.text
        chat_histories[user_id].append({"role": "model", "parts": [reply]})

        bot.reply_to(message, reply)

    except Exception as e:
        logger.error(f"Xato: {e}")
        bot.reply_to(message, "❌ Xatolik yuz berdi. Qayta urinib ko'ring yoki /clear bosing.")

logger.info("Bot ishga tushdi! 🚀")
bot.infinity_polling()
