import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient

# ================= CONFIG =================

BOT_TOKEN = "8435658476:AAEBER1zaUbZTJSRFtCJv2fRl24WqXDQSr4"

MONGO_URI = "mongodb+srv://cap1432:cap1432@cluster0.yllxk9g.mongodb.net/botydb?retryWrites=true&w=majority&appName=Cluster0"

ADMIN_ID = 1804574038
UPDATE_CHANNEL_ID = -1003157076350

# ================= BOT =================

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# ================= DATABASE =================

mongo = MongoClient(MONGO_URI)
db = mongo["botydb"]
users = db["users"]
withdraws = db["withdraws"]

# ================= HELPERS =================

def get_user(uid):
    user = users.find_one({"_id": uid})
    if not user:
        users.insert_one({
            "_id": uid,
            "balance": 0,
            "verified": 0
        })
        return get_user(uid)
    return user

# ================= KEYBOARDS =================

def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Verify Group", callback_data="verify")],
        [InlineKeyboardButton(text="👤 My Profile", callback_data="profile")],
        [InlineKeyboardButton(text="💬 Support", callback_data="support")]
    ])

def withdraw_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💸 Withdraw", callback_data="withdraw")]
    ])

# ================= START =================

@dp.message(F.text == "/start")
async def start(m: Message):
    get_user(m.from_user.id)
    await m.answer(
        "🤖 Welcome\nChoose option:",
        reply_markup=main_kb()
    )

# ================= PROFILE =================

@dp.callback_query(F.data == "profile")
async def profile(c):
    u = get_user(c.from_user.id)
    await c.message.answer(
        f"👤 ID: {c.from_user.id}\n"
        f"✅ Verified: {u['verified']}\n"
        f"💰 Balance: {u['balance']}",
        reply_markup=withdraw_kb()
    )
    await c.answer()

# ================= VERIFY (DUMMY OLD LOGIC) =================

@dp.callback_query(F.data == "verify")
async def verify(c):
    year = 2018  # dummy old year
    price = 10   # dummy earning

    users.update_one(
        {"_id": c.from_user.id},
        {"$inc": {"balance": price, "verified": 1}}
    )

    await c.message.answer(
        f"✅ Group Verified\n"
        f"📅 Year: {year}\n"
        f"💰 Earned: {price}"
    )
    await c.answer()

# ================= WITHDRAW =================

@dp.callback_query(F.data == "withdraw")
async def withdraw(c):
    u = get_user(c.from_user.id)

    if u["balance"] <= 0:
        await c.message.answer("❌ Balance zero")
        await c.answer()
        return

    withdraws.insert_one({
        "user": c.from_user.id,
        "amount": u["balance"],
        "status": "PENDING"
    })

    users.update_one(
        {"_id": c.from_user.id},
        {"$set": {"balance": 0}}
    )

    await bot.send_message(
        UPDATE_CHANNEL_ID,
        f"💸 Withdraw Request\n"
        f"User: {c.from_user.id}\n"
        f"Amount: {u['balance']}"
    )

    await c.message.answer("✅ Withdraw request sent")
    await c.answer()

# ================= SUPPORT =================

@dp.callback_query(F.data == "support")
async def support(c):
    await c.message.answer("✍️ Send your question")
    await c.answer()

@dp.message()
async def support_msg(m: Message):
    await bot.send_message(
        ADMIN_ID,
        f"📩 Support Message\n"
        f"User: {m.from_user.id}\n\n"
        f"{m.text}"
    )
    await m.answer("✅ Sent to admin")

# ================= RUN =================

async def main():
    print("🤖 Bot running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
