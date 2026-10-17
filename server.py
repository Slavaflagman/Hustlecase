import os
import sqlite3
import random
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

app = FastAPI(title="Hustle Case API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8840874512:AAHcjdgyFj5l6J-_oYk2PL_CafNfI6oQXB4")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- КАТАЛОГИ ВСЕХ 5 КЕЙСОВ И ЦЕНЫ ---

DEFAULT_CASE_GIFTS = [
    {"id": "gift_heart", "name": "Сердце", "price": 15, "image_url": "/src/heart.png"},
    {"id": "gift_bear", "name": "Мишка", "price": 15, "image_url": "/src/bear.png"},
    {"id": "gift_box", "name": "Подарочная коробка", "price": 25, "image_url": "/src/box.png"},
    {"id": "gift_rose", "name": "Роза", "price": 25, "image_url": "/src/rose.png"},
    {"id": "gift_cake", "name": "Торт", "price": 50, "image_url": "/src/cake.png"},
    {"id": "gift_rocket", "name": "Ракета", "price": 50, "image_url": "/src/rocket.png"},
    {"id": "gift_trophy", "name": "Кубок", "price": 100, "image_url": "/src/trophy.png"},
    {"id": "gift_ring", "name": "Кольцо", "price": 100, "image_url": "/src/ring.png"},
    {"id": "gift_diamond", "name": "Алмаз", "price": 100, "image_url": "/src/diamond.png"},
]

PREMIUM_CASE_GIFTS = [
    {"id": "gift_tulip", "name": "Тюльпан", "price": 25, "image_url": "/src/tulip.png"},
    {"id": "gift_rocket", "name": "Ракета", "price": 50, "image_url": "/src/rocket.png"},
    {"id": "gift_champagne", "name": "Шампанское", "price": 50, "image_url": "/src/champagne.png"},
    {"id": "nft_noodles", "name": "Лапша NFT", "price": 470, "image_url": "/src/noodles.png"},
    {"id": "nft_torch", "name": "Факел NFT", "price": 480, "image_url": "/src/torch.png"},
    {"id": "nft_icecream", "name": "Эскимо NFT", "price": 490, "image_url": "/src/icecream.png"},
    {"id": "nft_lollipop", "name": "Леденец NFT", "price": 500, "image_url": "/src/lollipop.png"},
]

PUMPKIN_CASE_GIFTS = [
    {"id": "gift_diamond", "name": "Алмаз", "price": 100, "image_url": "/src/diamond.png"},
    {"id": "gift_rocket", "name": "Ракета", "price": 50, "image_url": "/src/rocket.png"},
    {"id": "gift_champagne", "name": "Шампанское", "price": 50, "image_url": "/src/champagne.png"},
    {"id": "nft_torch", "name": "Факел NFT", "price": 480, "image_url": "/src/torch.png"},
    {"id": "nft_coffee", "name": "Стаканчик NFT", "price": 500, "image_url": "/src/coffee.png"},
    {"id": "nft_backpack", "name": "Рюкзак NFT", "price": 500, "image_url": "/src/backpack.png"},
    {"id": "nft_lantern", "name": "Фонарь NFT", "price": 620, "image_url": "/src/lantern.png"},
    {"id": "nft_mad_pumpkin", "name": "Mad Pumpkin NFT", "price": 1500, "image_url": "/src/pumpkin.png"},
]

SKULL_CASE_GIFTS = [
    {"id": "gift_trophy", "name": "Кубок", "price": 100, "image_url": "/src/trophy.png"},
    {"id": "gift_ring", "name": "Кольцо", "price": 100, "image_url": "/src/ring.png"},
    {"id": "gift_diamond", "name": "Алмаз", "price": 100, "image_url": "/src/diamond.png"},
    {"id": "nft_book", "name": "Книга NFT", "price": 550, "image_url": "/src/book.png"},
    {"id": "nft_jester", "name": "Колпак NFT", "price": 570, "image_url": "/src/jester.png"},
    {"id": "nft_medal", "name": "Медаль NFT", "price": 590, "image_url": "/src/medal.png"},
    {"id": "nft_sparkler", "name": "Искры NFT", "price": 612, "image_url": "/src/sparkler.png"},
    {"id": "nft_keycap", "name": "Клавиша NFT", "price": 628, "image_url": "/src/keycap.png"},
    {"id": "nft_mushroom", "name": "Гриб NFT", "price": 628, "image_url": "/src/mushroom.png"},
    {"id": "nft_cigar", "name": "Сигара NFT", "price": 1507, "image_url": "/src/cigar.png"},
    {"id": "nft_cats", "name": "Котики NFT", "price": 1972, "image_url": "/src/cats.png"},
    {"id": "nft_electric_skull", "name": "Electric Skull NFT", "price": 2500, "image_url": "/src/electric_skull.png"},
]

NFT_CASE_GIFTS = [
    {"id": "nft_lolpop", "name": "Lol Pop NFT", "price": 1211, "image_url": "/src/lolpop.png"},
    {"id": "nft_candle", "name": "Свеча NFT", "price": 1075, "image_url": "/src/candle.png"},
    {"id": "nft_key_heart", "name": "Сердце с ключом NFT", "price": 2107, "image_url": "/src/key_heart.png"},
    {"id": "nft_pumpkin_leg", "name": "Тыква NFT", "price": 1310, "image_url": "/src/pumpkin_leg.png"},
    {"id": "nft_skull_flower", "name": "Цветок с черепом NFT", "price": 1200, "image_url": "/src/skull_flower.png"},
    {"id": "nft_turntable", "name": "Проигрыватель NFT", "price": 1295, "image_url": "/src/turntable.png"},
    {"id": "nft_broom", "name": "Метла NFT", "price": 1265, "image_url": "/src/broom.png"},
    {"id": "nft_eagle", "name": "Кристальный орёл NFT", "price": 2601, "image_url": "/src/eagle.png"},
    {"id": "nft_ring_gold", "name": "Золотой перстень NFT", "price": 3317, "image_url": "/src/ring_gold.png"},
    {"id": "nft_voodoo", "name": "Кукла Вуду NFT", "price": 3497, "image_url": "/src/voodoo.png"},
    {"id": "nft_cigar_leg", "name": "Сигара NFT", "price": 3583, "image_url": "/src/cigar_leg.png"},
]

CASES_CONFIG = [
    {"id": "default", "name": "Default Case", "price": 75, "gifts": DEFAULT_CASE_GIFTS},
    {"id": "premium", "name": "Premium Case", "price": 199, "gifts": PREMIUM_CASE_GIFTS},
    {"id": "pumpkin", "name": "Pumpkin Case", "price": 349, "gifts": PUMPKIN_CASE_GIFTS},
    {"id": "skull", "name": "Skull Case", "price": 499, "gifts": SKULL_CASE_GIFTS},
    {"id": "nft", "name": "NFT Case", "price": 999, "gifts": NFT_CASE_GIFTS},
]

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY,
            total_deposits INTEGER DEFAULT 0,
            owner_profit REAL DEFAULT 0.0,
            payout_pool REAL DEFAULT 0.0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 0.0
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM stats")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO stats (id, total_deposits, owner_profit, payout_pool) VALUES (1, 0, 0, 0)")
    conn.commit()
    conn.close()

init_db()

class DepositRequest(BaseModel):
    user_id: int
    amount: int

class SpinRequest(BaseModel):
    user_id: int
    case_type: str
    is_demo: bool = False

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>index.html not found in root directory</h1>"

@app.get("/api/cases")
async def get_cases():
    return {"cases": CASES_CONFIG}

@app.post("/api/deposit")
async def process_deposit(req: DepositRequest):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    owner_share = req.amount * 0.60
    pool_share = req.amount * 0.40

    cursor.execute("""
        UPDATE stats 
        SET total_deposits = total_deposits + ?,
            owner_profit = owner_profit + ?,
            payout_pool = payout_pool + ?
        WHERE id = 1
    """, (req.amount, owner_share, pool_share))

    cursor.execute("""
        INSERT INTO users (user_id, balance) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET balance = balance + ?
    """, (req.user_id, req.amount, req.amount))

    conn.commit()
    conn.close()
    return {"status": "success", "added_balance": req.amount}

@app.post("/api/spin")
async def spin_case(req: SpinRequest):
    case_data = next((c for c in CASES_CONFIG if c["id"] == req.case_type), None)
    if not case_data:
        raise HTTPException(status_code=400, detail="Кейс не найден")
    
    catalog = case_data["gifts"]

    if req.is_demo:
        won_gift = random.choice(catalog)
        return {
            "status": "success",
            "is_demo": True,
            "won_gift": won_gift,
            "message": "Демо-прокрутка завершена!"
        }

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (req.user_id,))
    row = cursor.fetchone()
    user_balance = row[0] if row else 0

    if user_balance < case_data["price"]:
        conn.close()
        raise HTTPException(status_code=400, detail="Недостаточно средств на балансе")

    cursor.execute("SELECT payout_pool FROM stats WHERE id = 1")
    current_pool = cursor.fetchone()[0]

    allowed_gifts = [g for g in catalog if g["price"] <= current_pool]
    if not allowed_gifts:
        conn.close()
        return {
            "status": "no_pool",
            "won_gift": None,
            "message": "Пул выплат пополняется! Попробуйте позже."
        }

    won_gift = random.choice(allowed_gifts)

    cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (case_data["price"], req.user_id))

    try:
        await bot.send_gift(user_id=req.user_id, gift_id=won_gift["id"])
        cursor.execute("UPDATE stats SET payout_pool = payout_pool - ? WHERE id = 1", (won_gift["price"],))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Ошибка отправки подарка: {str(e)}")

    conn.close()
    return {
        "status": "success",
        "is_demo": False,
        "won_gift": won_gift,
        "message": f"Поздравляем! Вы выиграли {won_gift['name']}!"
    }

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (message.from_user.id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, 0)", (message.from_user.id,))
        conn.commit()
    conn.close()

    web_app_url = os.environ.get("WEB_APP_URL", "https://hustlecase-4.onrender.com/")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Открыть Hustle Case", web_app=WebAppInfo(url=web_app_url))]
    ])
    
    await message.answer(
        "Добро пожаловать в Hustle Case!\n\nОткрывай кейсы и испытывай удачу.",
        reply_markup=keyboard
    )

async def start_telegram_bot():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Bot polling error: {e}")

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(start_telegram_bot())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
