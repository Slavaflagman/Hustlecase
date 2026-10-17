import os
import sqlite3
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from aiogram import Bot

app = FastAPI(title="NFT case API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
bot = Bot(token=BOT_TOKEN)

# --- КАТАЛОГИ ВСЕХ 5 КЕЙСОВ БЕЗ КАРТИНОК ---

DEFAULT_CASE_GIFTS = [
    {"id": "gift_heart", "name": "Сердце", "price": 15},
    {"id": "gift_bear", "name": "Мишка", "price": 15},
    {"id": "gift_box", "name": "Подарочная коробка", "price": 25},
    {"id": "gift_rose", "name": "Роза", "price": 25},
    {"id": "gift_cake", "name": "Торт", "price": 50},
    {"id": "gift_rocket", "name": "Ракета", "price": 50},
    {"id": "gift_trophy", "name": "Кубок", "price": 100},
    {"id": "gift_ring", "name": "Кольцо", "price": 100},
    {"id": "gift_diamond", "name": "Алмаз", "price": 100},
]

PREMIUM_CASE_GIFTS = [
    {"id": "gift_tulip", "name": "Тюльпан", "price": 25},
    {"id": "gift_rocket", "name": "Ракета", "price": 50},
    {"id": "gift_champagne", "name": "Шампанское", "price": 50},
    {"id": "nft_noodles", "name": "Лапша NFT", "price": 470},
    {"id": "nft_torch", "name": "Факел NFT", "price": 480},
    {"id": "nft_icecream", "name": "Эскимо NFT", "price": 490},
    {"id": "nft_lollipop", "name": "Леденец NFT", "price": 500},
]

PUMPKIN_CASE_GIFTS = [
    {"id": "gift_diamond", "name": "Алмаз", "price": 100},
    {"id": "gift_rocket", "name": "Ракета", "price": 50},
    {"id": "gift_champagne", "name": "Шампанское", "price": 50},
    {"id": "nft_torch", "name": "Факел NFT", "price": 480},
    {"id": "nft_coffee", "name": "Стаканчик NFT", "price": 500},
    {"id": "nft_backpack", "name": "Рюкзак NFT", "price": 500},
    {"id": "nft_lantern", "name": "Фонарь NFT", "price": 620},
    {"id": "nft_mad_pumpkin", "name": "Mad Pumpkin NFT", "price": 1500},
]

SKULL_CASE_GIFTS = [
    {"id": "gift_trophy", "name": "Кубок", "price": 100},
    {"id": "gift_ring", "name": "Кольцо", "price": 100},
    {"id": "gift_diamond", "name": "Алмаз", "price": 100},
    {"id": "nft_book", "name": "Книга NFT", "price": 550},
    {"id": "nft_jester", "name": "Колпак NFT", "price": 570},
    {"id": "nft_medal", "name": "Медаль NFT", "price": 590},
    {"id": "nft_sparkler", "name": "Искры NFT", "price": 612},
    {"id": "nft_keycap", "name": "Клавиша NFT", "price": 628},
    {"id": "nft_mushroom", "name": "Гриб NFT", "price": 628},
    {"id": "nft_cigar", "name": "Сигара NFT", "price": 1507},
    {"id": "nft_cats", "name": "Котики NFT", "price": 1972},
    {"id": "nft_electric_skull", "name": "Electric Skull NFT", "price": 2500},
]

NFT_CASE_GIFTS = [
    {"id": "nft_lolpop", "name": "Lol Pop NFT", "price": 1211},
    {"id": "nft_candle", "name": "Свеча NFT", "price": 1075},
    {"id": "nft_key_heart", "name": "Сердце с ключом NFT", "price": 2107},
    {"id": "nft_pumpkin_leg", "name": "Тыква NFT", "price": 1310},
    {"id": "nft_skull_flower", "name": "Цветок с черепом NFT", "price": 1200},
    {"id": "nft_turntable", "name": "Проигрыватель NFT", "price": 1295},
    {"id": "nft_broom", "name": "Метла NFT", "price": 1265},
    {"id": "nft_eagle", "name": "Кристальный орёл NFT", "price": 2601},
    {"id": "nft_ring_gold", "name": "Золотой перстень NFT", "price": 3317},
    {"id": "nft_voodoo", "name": "Кукла Вуду NFT", "price": 3497},
    {"id": "nft_cigar_leg", "name": "Сигара NFT", "price": 3583},
]

# Общий список кейсов для фронтенда
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
    case_type: str = "default"

@app.get("/api/cases")
async def get_cases():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT payout_pool FROM stats WHERE id = 1")
    pool = cursor.fetchone()[0]
    conn.close()
    return {
        "payout_pool": round(pool, 2),
        "cases": CASES_CONFIG
    }

@app.get("/api/user/{user_id}")
async def get_user(user_id: int):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    balance = row[0] if row else 0.0
    conn.close()
    return {"user_id": user_id, "balance": balance}

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
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT payout_pool FROM stats WHERE id = 1")
    current_pool = cursor.fetchone()[0]

    if req.case_type == "premium":
        catalog = PREMIUM_CASE_GIFTS
        case_price = 199
    elif req.case_type == "pumpkin":
        catalog = PUMPKIN_CASE_GIFTS
        case_price = 349
    elif req.case_type == "skull":
        catalog = SKULL_CASE_GIFTS
        case_price = 499
    elif req.case_type == "nft":
        catalog = NFT_CASE_GIFTS
        case_price = 999
    else:
        catalog = DEFAULT_CASE_GIFTS
        case_price = 75

    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (req.user_id,))
    user_row = cursor.fetchone()
    user_balance = user_row[0] if user_row else 0.0

    if user_balance < case_price:
        conn.close()
        raise HTTPException(status_code=400, detail="Недостаточно звезд на балансе")

    new_user_balance = user_balance - case_price
    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_user_balance, req.user_id))

    allowed_gifts = [g for g in catalog if g["price"] <= current_pool]

    if not allowed_gifts:
        conn.close()
        return {
            "status": "no_pool",
            "won_gift": None,
            "new_balance": user_balance,
            "message": "Пул выплат пополняется! Попробуйте зайти чуть позже."
        }

    won_gift = random.choice(allowed_gifts)

    try:
        await bot.send_gift(
            user_id=req.user_id,
            gift_id=won_gift["id"]
        )
        cursor.execute("UPDATE stats SET payout_pool = payout_pool - ? WHERE id = 1", (won_gift["price"],))
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Ошибка отправки подарка: {str(e)}")

    conn.close()
    return {
        "status": "success",
        "won_gift": won_gift,
        "new_balance": new_user_balance,
        "message": f"Поздравляем! Вы выбили {won_gift['name']}!"
    }

@app.get("/api/stats")
async def get_stats():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT total_deposits, owner_profit, payout_pool FROM stats WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return {
        "total_deposits": row[0],
        "owner_profit_60": row[1],
        "payout_pool_40": row[2]
    }

app.mount("/", StaticFiles(directory=".", html=True), name="static")
