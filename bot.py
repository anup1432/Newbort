import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from pymongo import MongoClient

# ================== CONFIG (HARDCODED AS YOU ASKED) ==================

BOT_TOKEN = "8435658476:AAEBER1zaUbZTJSRFtCJv2fRl24WqXDQSr4"
ADMIN_ID = 1804574038
UPDATE_CHANNEL = -1003157076350

MONGO_URI = "mongodb+srv://cap1432:cap1432@cluster0.yllxk9g.mongodb.net/botydb?retryWrites=true&w=majority&appName=Cluster0"

# =====================================================================

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

mongo = MongoClient(MONGO_URI)
db = mongo["botydb"]
users = db["users"]

# ================== START ==================

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    uid = message.from_user.id

    if not users.find_one({"_id": uid}):
        users.insert_one({
            "_id": uid,
            "balance": 0,
            "verified": False
        })

    kb = [
        [types.KeyboardButton(text="📊 Balance")],
        [types.KeyboardButton(text="🆘 Support")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )

    await message.answer(
        "✅ Bot started successfully\n\nChoose an option:",
        reply_markup=keyboard
    )

# ================== BALANCE ==================

@dp.message(lambda m: m.text == "📊 Balance")
async def balance_cmd(message: types.Message):
    user = users.find_one({"_id": message.from_user.id})
    bal = user.get("balance", 0)
    await message.answer(f"💰 Your balance: {bal}")

# ================== SUPPORT ==================

@dp.message(lambda m: m.text == "🆘 Support")
async def support_cmd(message: types.Message):
    await message.answer("✍️ Send your question now:")

@dp.message()
async def forward_support(message: types.Message):
    if message.text in ["📊 Balance", "🆘 Support"]:
        return

    await bot.send_message(
        ADMIN_ID,
        f"📩 Support message\n\nFrom: {message.from_user.id}\n\n{message.text}"
    )
    await message.answer("✅ Your message sent to support")

# ================== ADMIN: ADD BALANCE ==================

@dp.message(Command("addbal"))
async def add_balance(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        _, uid, amt = message.text.split()
        uid = int(uid)
        amt = int(amt)

        users.update_one(
            {"_id": uid},
            {"$inc": {"balance": amt}}
        )
        await message.answer("✅ Balance added")

    except:
        await message.answer("❌ Use: /addbal user_id amount")

# ================== MAIN ==================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
