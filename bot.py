import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import google.generativeai as genai

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API kalitlar
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini sozlash
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Bot va Dispatcher
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Har foydalanuvchi uchun suhbat tarixi
chat_histories = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    user_name = message.from_user.first_name
    await message.answer(
        f"Assalomu alaykum, {user_name}! 👋\n\n"
        f"Men AI yordamchiman. Har qanday savolingizni bering!\n\n"
        f"📌 Komandalar:\n"
        f"/start - Boshlash\n"
        f"/help - Yordam\n"
        f"/clear - Suhbatni tozalash"
    )

@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "🤖 Men AI yordamchiman!\n\n"
        "✅ Nima qila olaman:\n"
        "- Savollarga javob berish\n"
        "- Matn yozish va tarjima qilish\n"
        "- Kod yozish\n"
        "- Maslahat berish\n"
        "- Suhbat qilish\n\n"
        "💬 Shunchaki xabar yozing!"
    )

@dp.message(Command("clear"))
async def clear(message: types.Message):
    user_id = message.from_user.id
    if user_id in chat_histories:
        del chat_histories[user_id]
    await message.answer("✅ Suhbat tarixi tozalandi!")

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user_text = message.text

    await bot.send_chat_action(message.chat.id, "typing")

    try:
        if user_id not in chat_histories:
            chat_histories[user_id] = []

        chat_histories[user_id].append({"role": "user", "parts": [user_text]})

        response = model.generate_content(chat_histories[user_id])
        reply = response.text

        chat_histories[user_id].append({"role": "model", "parts": [reply]})

        await message.answer(reply)

    except Exception as e:
        logger.error(f"Xato: {e}")
        await message.answer("❌ Xatolik yuz berdi. Qayta urinib ko'ring yoki /clear bosing.")

async def main():
    logger.info("Bot ishga tushdi! 🚀")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
