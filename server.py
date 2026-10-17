import asyncio
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import LabeledPrice, PreCheckoutQuery

# ---------------------------------------------------------
# НАСТРОЙКИ
# ---------------------------------------------------------
BOT_TOKEN = "ТВОЙ_ТОКЕН_БОТА_ИЗ_BOTFATHER"
ADMIN_ID = 8510236481

app = FastAPI()

# Разрешаем запросы с WebApp
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------------------------------------------------------
# БАЗА ДАННЫХ (SQLite)
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    # Таблица пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 0,
            total_deposited INTEGER DEFAULT 0
        )
    """)
    # Таблица глобальной кассы
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY,
            owner_profit INTEGER DEFAULT 0,
            payout_pool INTEGER DEFAULT 0
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO stats (id, owner_profit, payout_pool) VALUES (1, 0, 0)")
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------
# TELEGRAM BOT LOGIC (Приём реальных Stars)
# ---------------------------------------------------------
@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    payment = message.successful_payment
    stars_amount = payment.total_amount
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    owner_share = int(stars_amount * 0.60)
    pool_share = stars_amount - owner_share

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Обновляем или создаем юзера
    cursor.execute("""
        INSERT INTO users (user_id, username, balance, total_deposited)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            balance = balance + EXCLUDED.balance,
            total_deposited = total_deposited + EXCLUDED.total_deposited,
            username = EXCLUDED.username
    """, (user_id, username, stars_amount, stars_amount))

    # Начисляем кассу
    cursor.execute("""
        UPDATE stats SET owner_profit = owner_profit + ?, payout_pool = payout_pool + ? WHERE id = 1
    """, (owner_share, pool_share))

    conn.commit()
    conn.close()

    await message.answer(f"Успешно зачислено {stars_amount} Stars! Открывай WebApp и крути кейсы.")

# ---------------------------------------------------------
# API ДЛЯ WEBAPP (Связка с сайтом)
# ---------------------------------------------------------
class OpenCaseReq(BaseModel):
    user_id: int
    case_id: str

@app.get("/api/user/{user_id}")
async def get_user(user_id: int):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance, total_deposited FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {"balance": 0, "total_deposited": 0}
    return {"balance": row[0], "total_deposited": row[1]}

@app.get("/api/admin/stats")
async def get_admin_stats(admin_id: int):
    if admin_id != ADMIN_ID:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT owner_profit, payout_pool FROM stats WHERE id = 1")
    stats_row = cursor.fetchone()
    
    cursor.execute("SELECT user_id, username, balance, total_deposited FROM users ORDER BY total_deposited DESC")
    users_rows = cursor.fetchall()
    conn.close()

    return {
        "owner_profit": stats_row[0],
        "payout_pool": stats_row[1],
        "users": [{"id": r[0], "username": r[1], "balance": r[2], "deposited": r[3]} for r in users_rows]
    }

# Функция для вызова создания счета из WebApp
@app.post("/api/create-invoice")
async def create_invoice(user_id: int, amount: int):
    link = await bot.create_invoice_link(
        title="Пополнение баланса",
        description=f"Зачисление {amount} Stars в Hustle Gifts",
        payload=f"topup_{user_id}_{amount}",
        currency="XTR",
        prices=[LabeledPrice(label="Stars", amount=amount)]
    )
    return {"invoice_link": link}
