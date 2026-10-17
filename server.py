import os
import sqlite3
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from aiogram import Bot, Dispatcher, types
from aiogram.types import LabeledPrice

app = FastAPI(title="Hustle Case API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BOT_TOKEN = "8840874512:AAHcjdgyFj5l6J-_oYk2PL_CafNfI6oQXB4"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            gift_name TEXT,
            gift_price INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY,
            total_deposits INTEGER DEFAULT 0,
            owner_profit REAL DEFAULT 0,
            payout_pool REAL DEFAULT 0
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO stats (id, total_deposits, owner_profit, payout_pool) VALUES (1, 0, 0, 0)")
    conn.commit()
    conn.close()

init_db()

# Каталоги кейсов
CASES = [
    {
        "id": "default",
        "name": "Default Case",
        "price": 75,
        "gifts": [
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
    },
    {
        "id": "premium",
        "name": "Premium Case",
        "price": 199,
        "gifts": [
            {"id": "gift_tulip", "name": "Тюльпан", "price": 25},
            {"id": "gift_rocket", "name": "Ракета", "price": 50},
            {"id": "gift_champagne", "name": "Шампанское", "price": 50},
            {"id": "nft_noodles", "name": "Лапша NFT", "price": 470},
            {"id": "nft_torch", "name": "Факел NFT", "price": 480},
            {"id": "nft_icecream", "name": "Эскимо NFT", "price": 490},
            {"id": "nft_lollipop", "name": "Леденец NFT", "price": 500},
        ]
    },
    {
        "id": "pumpkin",
        "name": "Pumpkin Case",
        "price": 349,
        "gifts": [
            {"id": "gift_diamond", "name": "Алмаз", "price": 100},
            {"id": "gift_rocket", "name": "Ракета", "price": 50},
            {"id": "gift_champagne", "name": "Шампанское", "price": 50},
            {"id": "nft_torch", "name": "Факел NFT", "price": 480},
            {"id": "nft_coffee", "name": "Стаканчик NFT", "price": 500},
            {"id": "nft_backpack", "name": "Рюкзак NFT", "price": 500},
            {"id": "nft_lantern", "name": "Фонарь NFT", "price": 620},
            {"id": "nft_mad_pumpkin", "name": "Mad Pumpkin NFT", "price": 1500},
        ]
    },
    {
        "id": "skull",
        "name": "Skull Case",
        "price": 499,
        "gifts": [
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
    },
    {
        "id": "nft",
        "name": "NFT Case",
        "price": 999,
        "gifts": [
            {"id": "nft_lolpop", "name": "Lol Pop NFT", "price": 1211},
            {"id": "nft_cigar", "name": "Сигара NFT", "price": 1507},
            {"id": "nft_cats", "name": "Котики NFT", "price": 1972},
            {"id": "nft_electric_skull", "name": "Electric Skull NFT", "price": 2500},
        ]
    }
]

class InvoiceRequest(BaseModel):
    user_id: int
    amount: int

class SpinRequest(BaseModel):
    user_id: int
    case_id: str
    is_demo: bool

@app.get("/api/cases")
async def get_cases():
    return {"cases": CASES}

@app.get("/api/user/{user_id}")
async def get_user(user_id: int):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    balance = row[0] if row else 0

    cursor.execute("SELECT gift_name, gift_price FROM inventory WHERE user_id = ? ORDER BY id DESC", (user_id,))
    inv = [{"name": r[0], "price": r[1]} for r in cursor.fetchall()]
    conn.close()
    return {"balance": balance, "inventory": inv}

@app.post("/api/create-invoice")
async def create_invoice(req: InvoiceRequest):
    try:
        prices = [LabeledPrice(label="Пополнение баланса", amount=req.amount)]
        invoice_link = await bot.create_invoice_link(
            title="Пополнение баланса",
            description=f"Пополнение на {req.amount} ⭐ в Hustle Case",
            payload=f"topup_{req.user_id}_{req.amount}",
            currency="XTR",
            prices=prices
        )
        return {"invoice_link": invoice_link}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/spin")
async def spin_case(req: SpinRequest):
    case = next((c for c in CASES if c["id"] == req.case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Кейс не найден")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (req.user_id,))
    row = cursor.fetchone()
    balance = row[0] if row else 0

    if not req.is_demo:
        if balance < case["price"]:
            conn.close()
            raise HTTPException(status_code=400, detail="Недостаточно звезд на балансе")
        
        # Списываем баланс
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (case["price"], req.user_id))
        
        # Распределение 60% / 40% в статистику
        owner_cut = case["price"] * 0.60
        pool_cut = case["price"] * 0.40
        cursor.execute("UPDATE stats SET owner_profit = owner_profit + ?, payout_pool = payout_pool + ? WHERE id = 1", (owner_cut, pool_cut))

    won_gift = random.choice(case["gifts"])

    if not req.is_demo:
        cursor.execute("INSERT INTO inventory (user_id, gift_name, gift_price) VALUES (?, ?, ?)", 
                       (req.user_id, won_gift["name"], won_gift["price"]))
        conn.commit()

    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (req.user_id,))
    new_balance = cursor.fetchone()[0]
    conn.close()

    return {"won_gift": won_gift, "new_balance": new_balance}
