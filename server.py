import os
import sqlite3
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

# Твой токен бота
BOT_TOKEN = "8840874512:AAHcjdgyFj5l6J-_oYk2PL_CafNfI6oQXB4"
bot = Bot(token=BOT_TOKEN)

# --- КАТАЛОГИ ВСЕХ 5 КЕЙСОВ ДЛЯ NFT CASE ---

# 1. Default Case (75 Stars)
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

# 2. Premium Case (199 Stars)
PREMIUM_CASE_GIFTS = [
    {"id": "gift_tulip", "name": "Тюльпан", "price": 25, "image_url": "/src/tulip.png"},
    {"id": "gift_rocket", "name": "Ракета", "price": 50, "image_url": "/src/rocket.png"},
    {"id": "gift_champagne", "name": "Шампанское", "price": 50, "image_url": "/src/champagne.png"},
    {"id": "nft_noodles", "name": "Лапша NFT", "price": 470, "image_url": "/src/noodles.png"},
    {"id": "nft_torch", "name": "Факел NFT", "price": 480, "image_url": "/src/torch.png"},
    {"id": "nft_icecream", "name": "Эскимо NFT", "price": 490, "image_url": "/src/icecream.png"},
    {"id": "nft_lollipop", "name": "Леденец NFT", "price": 500, "image_url": "/src/lollipop.png"},
]

# 3. Pumpkin Case (349 Stars)
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

# 4. Skull Case (499 Stars)
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

# 5. Legendary Case (999 Stars)
LEGENDARY_CASE_GIFTS = [
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
    case_type: str = "default"  # "default", "premium", "pumpkin", "skull", "legendary"

@app.post("/api/deposit")
async def process_deposit(req: DepositRequest):
    """Фиксация доната: 60% — владельцу, 40% — в пул выплат NFT case"""
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
    """Прокрут кейса с защитой бюджета по 40% пулу кассы"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT payout_pool FROM stats WHERE id = 1")
    current_pool = cursor.fetchone()[0]

    if req.case_type == "premium":
        catalog = PREMIUM_CASE_GIFTS
    elif req.case_type == "pumpkin":
        catalog = PUMPKIN_CASE_GIFTS
    elif req.case_type == "skull":
        catalog = SKULL_CASE_GIFTS
    elif req.case_type == "legendary":
        catalog = LEGENDARY_CASE_GIFTS
    else:
        catalog = DEFAULT_CASE_GIFTS

    allowed_gifts = [g for g in catalog if g["price"] <= current_pool]

    if not allowed_gifts:
        conn.close()
        return {
            "status": "no_pool",
            "won_gift": None,
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
        conn.close()
        raise HTTPException(status_code=500, detail=f"Ошибка отправки подарка: {str(e)}")

    conn.close()
    return {
        "status": "success",
        "won_gift": won_gift,
        "message": f"Поздравляем! Вы выбили {won_gift['name']}!"
    }

@app.get("/api/stats")
async def get_stats():
    """Касса владельца NFT case"""
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
