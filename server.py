import os
import sqlite3
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

app = FastAPI(title="Hustle Case API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8840874512:AAHcjdgyFj5l6J-_oYk2PL_CafNfI6oQXB4")
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "8510236481"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчик /start: ссылки на канал и кнопка с новой ссылкой на Render
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    web_app_url = "https://hustlecase-17.onrender.com/?v=2"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Открыть Hustle Case", 
                    web_app=WebAppInfo(url=web_app_url)
                )
            ]
        ]
    )
    
    caption_text = (
        "📢 Наш канал: https://t.me/hustlecaseInfo\n"
        "🤖 Бот: https://t.me/HustleCaseBot"
    )
    
    await message.answer(caption_text, reply_markup=keyboard)

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

# Каталог кейсов
CASES = [
    {
        "id": "default",
        "name": "Default Case",
        "price": 75,
        "gifts": [
            {"id": "gift_heart", "name": "Heart", "price": 15},
            {"id": "gift_bear", "name": "Teddy Bear", "price": 15},
            {"id": "gift_box", "name": "Gift Box", "price": 25},
            {"id": "gift_rose", "name": "Rose", "price": 25},
            {"id": "gift_cake", "name": "Cake", "price": 50},
            {"id": "gift_rocket", "name": "Rocket", "price": 50},
            {"id": "gift_trophy", "name": "Trophy", "price": 100},
            {"id": "gift_ring", "name": "Ring", "price": 100},
            {"id": "gift_diamond", "name": "Diamond", "price": 100},
        ]
    },
    {
        "id": "premium",
        "name": "Premium Case",
        "price": 199,
        "gifts": [
            {"id": "gift_tulip", "name": "Tulip", "price": 25},
            {"id": "gift_rocket", "name": "Rocket", "price": 50},
            {"id": "gift_champagne", "name": "Champagne", "price": 50},
            {"id": "nft_noodles", "name": "Noodles NFT", "price": 470},
            {"id": "nft_torch", "name": "Torch NFT", "price": 480},
            {"id": "nft_icecream", "name": "Ice Cream NFT", "price": 490},
            {"id": "nft_lollipop", "name": "Lollipop NFT", "price": 500},
        ]
    },
    {
        "id": "pumpkin",
        "name": "Pumpkin Case",
        "price": 349,
        "gifts": [
            {"id": "gift_diamond", "name": "Diamond", "price": 100},
            {"id": "gift_rocket", "name": "Rocket", "price": 50},
            {"id": "gift_champagne", "name": "Champagne", "price": 50},
            {"id": "nft_torch", "name": "Torch NFT", "price": 480},
            {"id": "nft_coffee", "name": "Coffee Cup NFT", "price": 500},
            {"id": "nft_backpack", "name": "Backpack NFT", "price": 500},
            {"id": "nft_lantern", "name": "Lantern NFT", "price": 620},
            {"id": "nft_mad_pumpkin", "name": "Mad Pumpkin NFT", "price": 1500},
        ]
    },
    {
        "id": "skull",
        "name": "Skull Case",
        "price": 499,
        "gifts": [
            {"id": "gift_trophy", "name": "Trophy", "price": 100},
            {"id": "gift_ring", "name": "Ring", "price": 100},
            {"id": "gift_diamond", "name": "Diamond", "price": 100},
            {"id": "nft_book", "name": "Book NFT", "price": 550},
            {"id": "nft_jester", "name": "Jester Cap NFT", "price": 570},
            {"id": "nft_medal", "name": "Medal NFT", "price": 590},
            {"id": "nft_sparkler", "name": "Sparkler NFT", "price": 612},
            {"id": "nft_keycap", "name": "Keycap NFT", "price": 628},
            {"id": "nft_mushroom", "name": "Mushroom NFT", "price": 628},
            {"id": "nft_cigar", "name": "Cigar NFT", "price": 1507},
            {"id": "nft_cats", "name": "Cats NFT", "price": 1972},
            {"id": "nft_electric_skull", "name": "Electric Skull NFT", "price": 2500},
        ]
    },
    {
        "id": "nft",
        "name": "NFT Case",
        "price": 999,
        "gifts": [
            {"id": "nft_candle", "name": "Heart Candle NFT", "price": 1075},
            {"id": "nft_heart_locket", "name": "Heart Locket NFT", "price": 2107},
            {"id": "nft_pumpkin_new", "name": "Mad Pumpkin NFT", "price": 1310},
            {"id": "nft_skull_flower", "name": "Skull Flower NFT", "price": 1200},
            {"id": "nft_cigar_new", "name": "Cigar NFT", "price": 3583},
            {"id": "nft_crystal_eagle", "name": "Crystal Eagle NFT", "price": 2601},
            {"id": "nft_gramophone", "name": "Gramophone NFT", "price": 1295},
            {"id": "nft_broom", "name": "Witch Broom NFT", "price": 1265},
            {"id": "nft_voodoo", "name": "Voodoo Doll NFT", "price": 3497},
            {"id": "nft_telegram_ring", "name": "Telegram Ring NFT", "price": 3317},
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

@app.get("/", response_class=HTMLResponse)
async def read_index():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>index.html file not found!</h1>"

@app.get("/api/cases")
async def get_cases():
    return {"cases": CASES}

@app.get("/api/user/{user_id}")
async def get_user(user_id: int):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    cursor.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)", (user_id,))
    conn.commit()

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
        prices = [LabeledPrice(label="Top-up balance", amount=req.amount)]
        invoice_link = await bot.create_invoice_link(
            title="Balance Top-up",
            description=f"Top-up {req.amount} ⭐ in Hustle Case",
            payload=f"topup_{req.user_id}_{req.amount}",
            currency="XTR",
            prices=prices
        )
        
        try:
            await bot.send_message(ADMIN_TELEGRAM_ID, f"🔔 New deposit invoice!\n👤 User: <code>{req.user_id}</code>\n💰 Amount: <b>{req.amount} ⭐</b>", parse_mode="HTML")
        except:
            pass

        return {"invoice_link": invoice_link}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/spin")
async def spin_case(req: SpinRequest):
    case = next((c for c in CASES if c["id"] == req.case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (req.user_id,))
    row = cursor.fetchone()
    balance = row[0] if row else 0

    if not req.is_demo:
        if balance < case["price"]:
            conn.close()
            raise HTTPException(status_code=400, detail="Insufficient Stars balance")
        
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (case["price"], req.user_id))
        
        owner_cut = case["price"] * 0.60
        pool_cut = case["price"] * 0.40
        cursor.execute("UPDATE stats SET owner_profit = owner_profit + ?, payout_pool = payout_pool + ? WHERE id = 1", (owner_cut, pool_cut))

    cursor.execute("SELECT payout_pool FROM stats WHERE id = 1")
    stats_row = cursor.fetchone()
    payout_pool = stats_row[0] if stats_row else 0

    pool_contribution = case["price"] * 0.40
    max_allowed_prize = payout_pool + pool_contribution

    safe_gifts = [g for g in case["gifts"] if req.is_demo or g["price"] <= max_allowed_prize]
    if not safe_gifts:
        safe_gifts = [min(case["gifts"], key=lambda x: x["price"])]

    won_gift = random.choice(safe_gifts)

    if not req.is_demo:
        cursor.execute("UPDATE stats SET payout_pool = MAX(0, payout_pool - ?) WHERE id = 1", (won_gift["price"],))
        cursor.execute("INSERT INTO inventory (user_id, gift_name, gift_price) VALUES (?, ?, ?)", 
                       (req.user_id, won_gift["name"], won_gift["price"]))
        conn.commit()

        try:
            await bot.send_message(ADMIN_TELEGRAM_ID, f"🎁 Case opened!\n👤 User: <code>{req.user_id}</code>\n📦 Case: <b>{case['name']}</b>\n🏆 Won: <b>{won_gift['name']} ({won_gift['price']} ⭐)</b>", parse_mode="HTML")
        except:
            pass

    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (req.user_id,))
    new_balance = cursor.fetchone()[0]
    conn.close()

    tape = [random.choice(case["gifts"]) for _ in range(35)]
    winner_index = 25
    tape[winner_index] = won_gift
    tape.extend([random.choice(case["gifts"]) for _ in range(5)])

    return {
        "won_gift": won_gift, 
        "new_balance": new_balance,
        "roulette_tape": tape,
        "winner_index": winner_index
    }
