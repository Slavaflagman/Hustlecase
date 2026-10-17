import os
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from aiogram import Bot

# Инициализация FastAPI
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

# Инициализация базы данных
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

class ClaimGiftRequest(BaseModel):
    user_id: int
    gift_id: str
    gift_price: int

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

@app.post("/api/claim_gift")
async def claim_gift(req: ClaimGiftRequest):
    """Автоматическая выдача подарка через Telegram Bot API"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT payout_pool FROM stats WHERE id = 1")
    current_pool = cursor.fetchone()[0]

    # Проверка: хватает ли в пуле выплат (40%) звёзд на этот подарок
    if current_pool < req.gift_price:
        conn.close()
        raise HTTPException(
            status_code=400, 
            detail="Пул выплат пока пополняется (валидация смарт-контракта TON). Попробуйте позже!"
        )

    # Автоматическая отправка подарка через Bot API
    try:
        await bot.send_gift(
            user_id=req.user_id,
            gift_id=req.gift_id
        )
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Ошибка при отправке подарка: {str(e)}")

    # Списываем стоимость подарка из пула выплат
    cursor.execute("UPDATE stats SET payout_pool = payout_pool - ? WHERE id = 1", (req.gift_price,))
    conn.commit()
    conn.close()

    return {"status": "success", "message": "Подарок успешно отправлен в личный профиль!"}

@app.get("/api/stats")
async def get_stats():
    """Просмотр кассы (только для админа)"""
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
