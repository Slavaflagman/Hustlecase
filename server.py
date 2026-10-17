import os
import sqlite3
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from aiogram import Bot

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
bot = Bot(token=BOT_TOKEN)

# Список всех доступных NFT-подарков и их стоимость в Stars
GIFTS_CATALOG = [
    {"id": "gift_cheap_1", "name": "Star", "price": 15},
    {"id": "gift_cheap_2", "name": "Heart", "price": 50},
    {"id": "gift_medium_1", "name": "Bear", "price": 100},
    {"id": "gift_medium_2", "name": "Trophy", "price": 350},
    {"id": "gift_expensive_1", "name": "NFT Rocket", "price": 1000},
    {"id": "gift_expensive_2", "name": "NFT Crown", "price": 3500},
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
    case_price: int

@app.post("/api/deposit")
async def process_deposit(req: DepositRequest):
    """Фиксация доната: 60% — владельцу, 40% — в пул выплат"""
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
    """Прокрут кейса с динамическим подбором выигрыша под бюджет пула"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Списываем стоимость прокрута с баланса игрока (или проверяем оплату)
    cursor.execute("SELECT payout_pool FROM stats WHERE id = 1")
    current_pool = cursor.fetchone()[0]

    # Фильтруем подарки: оставляем ТОЛЬКО ТЕ, на которые хватает денег в 40% пуле
    allowed_gifts = [g for g in GIFTS_CATALOG if g["price"] <= current_pool]

    if not allowed_gifts:
        # Если в пуле совсем нет денег даже на самый дешевый гифт
        conn.close()
        return {
            "status": "no_pool",
            "won_gift": None,
            "message": "Пул выплат пополняется! Попробуйте зайти чуть позже."
        }

    # Случайным образом выбираем подарок из доступных по бюджету
    won_gift = random.choice(allowed_gifts)

    # Автоматически отправляем подарок победителю через Bot API
    try:
        await bot.send_gift(
            user_id=req.user_id,
            gift_id=won_gift["id"]
        )
        # Списываем стоимость выпавшего подарка из пула
        cursor.execute("UPDATE stats SET payout_pool = payout_pool - ? WHERE id = 1", (won_gift["price"],))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Ошибка отправки подарка: {str(e)}")

    conn.close()
    return {
        "status": "success",
        "won_gift": won_gift,
        "message": f"Поздравляем! Вы выбили {won_gift['name']} за {won_gift['price']} Stars!"
    }

@app.get("/api/stats")
async def get_stats():
    """Просмотр кассы (только для владельца)"""
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

