import os
import sqlite3
import random
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
import uvicorn

app = FastAPI(title="Hustle Case API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8840874512:AAHcjdgyFj5l6J-_oYk2PL_CafNfI6oQXB4")
WEB_APP_URL = "https://hustlecase-4.onrender.com/"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    args = message.text.split()
    referrer_id = None
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referrer_id = int(args[1].replace("ref_", ""))
        except:
            pass

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (message.from_user.id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id, real_stars, game_stars, referrer_id) VALUES (?, 100, 500, ?)", 
                       (message.from_user.id, referrer_id))
        conn.commit()
    conn.close()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть Hustle Case", web_app=WebAppInfo(url=WEB_APP_URL))]
    ])
    await message.answer(
        "Добро пожаловать в Hustle Case!\n\n"
        "Открывай кейсы, играй в Краш и выигрывай NFT-подарки.",
        reply_markup=keyboard
    )

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
            real_stars REAL DEFAULT 0.0,
            game_stars REAL DEFAULT 0.0,
            referrer_id INTEGER DEFAULT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_name TEXT,
            item_price REAL
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM stats")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO stats (id, total_deposits, owner_profit, payout_pool) VALUES (1, 0, 0, 5000)")
    conn.commit()
    conn.close()

init_db()

GORILLA_GIFTS = [
    {"id": "nft_voodoo", "name": "Вуду NFT", "price": 3737},
    {"id": "nft_ring", "name": "Перстень NFT", "price": 3374},
    {"id": "nft_key_heart", "name": "Сердце с ключом", "price": 2270},
    {"id": "nft_eagle", "name": "Кристальный орёл", "price": 1570},
    {"id": "nft_flower", "name": "Цветок с черепом", "price": 1109},
    {"id": "nft_eye", "name": "Око NFT", "price": 864},
    {"id": "nft_socks", "name": "Носки NFT", "price": 524},
    {"id": "nft_lantern", "name": "Фонарь NFT", "price": 523},
    {"id": "nft_2025", "name": "2025 NFT", "price": 445},
    {"id": "gift_star5", "name": "5 Звёзд", "price": 5},
]

CASES_CONFIG = [
    {"id": "gorilla", "name": "Gorilla Case", "price": 249, "gifts": GORILLA_GIFTS}
]

class ExchangeRequest(BaseModel):
    user_id: int
    amount: int

class SpinRequest(BaseModel):
    user_id: int
    case_type: str = "gorilla"
    is_demo: bool = False

class CrashRequest(BaseModel):
    user_id: int
    bet: int
    target_multiplier: float

@app.get("/api/cases")
async def get_cases():
    return {"cases": CASES_CONFIG}

@app.get("/api/user/{user_id}")
async def get_user(user_id: int):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT real_stars, game_stars FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users (user_id, real_stars, game_stars) VALUES (?, 100, 500)", (user_id,))
        conn.commit()
        real_stars, game_stars = 100, 500
    else:
        real_stars, game_stars = row[0], row[1]

    cursor.execute("SELECT item_name, item_price FROM inventory WHERE user_id = ?", (user_id,))
    items = [{"name": r[0], "price": r[1]} for r in cursor.fetchall()]

    conn.close()
    return {
        "user_id": user_id, 
        "real_stars": real_stars, 
        "game_stars": game_stars,
        "inventory": items
    }

@app.post("/api/exchange")
async def exchange_stars(req: ExchangeRequest):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT real_stars FROM users WHERE user_id = ?", (req.user_id,))
    row = cursor.fetchone()
    user_stars = row[0] if row else 0

    if user_stars < req.amount:
        conn.close()
        raise HTTPException(status_code=400, detail="Недостаточно реальных звёзд")

    cursor.execute("""
        UPDATE users 
        SET real_stars = real_stars - ?, game_stars = game_stars + ? 
        WHERE user_id = ?
    """, (req.amount, req.amount, req.user_id))
    
    conn.commit()
    conn.close()
    return {"status": "success", "exchanged": req.amount}

@app.post("/api/spin")
async def spin_case(req: SpinRequest):
    case_cfg = CASES_CONFIG[0]
    case_price = case_cfg["price"]
    catalog = case_cfg["gifts"]

    if req.is_demo:
        won_gift = random.choice(catalog)
        return {"status": "success", "is_demo": True, "won_gift": won_gift}

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT game_stars FROM users WHERE user_id = ?", (req.user_id,))
    row = cursor.fetchone()
    game_stars = row[0] if row else 0

    if game_stars < case_price:
        conn.close()
        raise HTTPException(status_code=400, detail="Недостаточно игровых звёзд")

    cursor.execute("UPDATE users SET game_stars = game_stars - ? WHERE user_id = ?", (case_price, req.user_id))
    cursor.execute("SELECT payout_pool FROM stats WHERE id = 1")
    current_pool = cursor.fetchone()[0]

    allowed_gifts = [g for g in catalog if g["price"] <= current_pool]
    if not allowed_gifts:
        allowed_gifts = [catalog[-1]]

    won_gift = random.choice(allowed_gifts)

    cursor.execute("INSERT INTO inventory (user_id, item_name, item_price) VALUES (?, ?, ?)",
                   (req.user_id, won_gift["name"], won_gift["price"]))

    try:
        await bot.send_gift(user_id=req.user_id, gift_id=won_gift["id"])
        cursor.execute("UPDATE stats SET payout_pool = payout_pool - ? WHERE id = 1", (won_gift["price"],))
    except Exception:
        pass

    conn.commit()
    conn.close()
    return {"status": "success", "is_demo": False, "won_gift": won_gift}

@app.post("/api/crash/play")
async def play_crash(req: CrashRequest):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT game_stars FROM users WHERE user_id = ?", (req.user_id,))
    row = cursor.fetchone()
    game_stars = row[0] if row else 0

    if game_stars < req.bet or req.bet <= 0:
        conn.close()
        raise HTTPException(status_code=400, detail="Недостаточно звёзд")

    new_stars = game_stars - req.bet
    crash_mult = round(max(1.00, 0.94 / (1.0 - random.random())), 2)
    won = req.target_multiplier <= crash_mult
    payout = int(req.bet * req.target_multiplier) if won else 0

    if won:
        new_stars += payout

    cursor.execute("UPDATE users SET game_stars = ? WHERE user_id = ?", (new_stars, req.user_id))
    conn.commit()
    conn.close()

    return {"crashed_at": crash_mult, "won": won, "payout": payout, "new_stars": new_stars}

app.mount("/", StaticFiles(directory=".", html=True), name="static")

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(dp.start_polling(bot))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
