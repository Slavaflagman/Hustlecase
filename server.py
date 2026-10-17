import sqlite3
import random
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

# --- БАЗА ДАННЫХ ---
def init_db():
    conn = sqlite3.connect("hustlecase.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS economy (
            key TEXT PRIMARY KEY,
            value REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            game_type TEXT,
            item_name TEXT,
            bet_amount INTEGER,
            payout INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO economy (key, value) VALUES ('payout_pool', 0.0)")
    conn.commit()
    conn.close()

init_db()

# --- КАТАЛОГ ИЗ 5 КЕЙСОВ ---
CASES = [
    {"id": 1, "name": "Default Case", "price": 50, "prizes": [("Sticker Pack", 10), ("10 Stars", 10), ("Пусто", 30)]},
    {"id": 2, "name": "Standard Case", "price": 150, "prizes": [("Telegram Premium", 100), ("50 Stars", 50), ("Пусто", 100)]},
    {"id": 3, "name": "Silver Case", "price": 300, "prizes": [("Rare Collectible", 220), ("100 Stars", 120), ("Пусто", 180)]},
    {"id": 4, "name": "Gold Case", "price": 600, "prizes": [("Epic Collectible", 450), ("300 Stars", 250), ("Пусто", 350)]},
    {"id": 5, "name": "Legendary Case", "price": 1500, "prizes": [("Unique Durov Item", 1100), ("1000 Stars", 700)]}
]

@app.get("/api/cases")
def get_cases():
    conn = sqlite3.connect("hustlecase.db")
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM economy WHERE key = 'payout_pool'")
    pool = cursor.fetchone()[0]
    conn.close()
    return {"payout_pool": round(pool, 2), "cases": CASES}

@app.get("/api/user/{user_id}")
def get_user(user_id: int):
    conn = sqlite3.connect("hustlecase.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    balance = user[0] if user else 0
    conn.close()
    return {"user_id": user_id, "balance": balance}

class TopUpRequest(BaseModel):
    user_id: int
    amount: int

@app.post("/api/user/topup")
def topup_user(data: TopUpRequest):
    conn = sqlite3.connect("hustlecase.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET balance = balance + ?", 
                   (data.user_id, data.amount, data.amount))
    conn.commit()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (data.user_id,))
    new_bal = cursor.fetchone()[0]
    conn.close()
    return {"success": True, "balance": new_bal}

class SpinRequest(BaseModel):
    user_id: int
    case_id: int

@app.post("/api/spin")
def spin_case(data: SpinRequest):
    conn = sqlite3.connect("hustlecase.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (data.user_id,))
    user = cursor.fetchone()
    user_balance = user[0] if user else 0
    
    case = next((c for c in CASES if c["id"] == data.case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Кейс не найден")
        
    if user_balance < case["price"]:
        raise HTTPException(status_code=400, detail="Недостаточно реальных звезд")

    new_user_balance = user_balance - case["price"]
    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_user_balance, data.user_id))

    pool_cut = case["price"] * 0.40
    cursor.execute("UPDATE economy SET value = value + ? WHERE key = 'payout_pool'", (pool_cut,))
    
    cursor.execute("SELECT value FROM economy WHERE key = 'payout_pool'")
    current_pool = cursor.fetchone()[0]

    valid_prizes = [p for p in case["prizes"] if p[1] == 0 or p[1] <= current_pool]
    if not valid_prizes:
        valid_prizes = [("Утешительный бонус", 0)]

    won_prize, prize_cost = random.choice(valid_prizes)

    if prize_cost > 0:
        cursor.execute("UPDATE economy SET value = value - ? WHERE key = 'payout_pool'", (prize_cost,))

    cursor.execute(
        "INSERT INTO transactions (user_id, game_type, item_name, bet_amount, payout) VALUES (?, 'case', ?, ?, ?)",
        (data.user_id, won_prize, case["price"], prize_cost)
    )
    conn.commit()
    conn.close()

    return {"success": True, "prize": won_prize, "prize_cost": prize_cost, "new_balance": new_user_balance}

class CrashPlayRequest(BaseModel):
    user_id: int
    bet: int
    target_multiplier: float

@app.post("/api/crash/play")
def play_crash(data: CrashPlayRequest):
    conn = sqlite3.connect("hustlecase.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (data.user_id,))
    user = cursor.fetchone()
    user_balance = user[0] if user else 0
    
    if user_balance < data.bet or data.bet <= 0:
        raise HTTPException(status_code=400, detail="Недостаточно средств")
        
    new_balance = user_balance - data.bet
    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, data.user_id))
    
    pool_cut = data.bet * 0.40
    cursor.execute("UPDATE economy SET value = value + ? WHERE key = 'payout_pool'", (pool_cut,))
    
    crash_multiplier = round(max(1.00, 0.93 / (1.0 - random.random())), 2)
    
    won = data.target_multiplier <= crash_multiplier
    payout = 0
    
    if won:
        payout = int(data.bet * data.target_multiplier)
        cursor.execute("SELECT value FROM economy WHERE key = 'payout_pool'")
        current_pool = cursor.fetchone()[0]
        
        net_payout = payout - data.bet
        if net_payout <= current_pool:
            if net_payout > 0:
                cursor.execute("UPDATE economy SET value = value - ? WHERE key = 'payout_pool'", (net_payout,))
            new_balance += payout
            cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, data.user_id))
        else:
            won = False
            payout = 0
            crash_multiplier = max(1.01, round(data.target_multiplier - 0.05, 2))

    cursor.execute(
        "INSERT INTO transactions (user_id, game_type, item_name, bet_amount, payout) VALUES (?, 'crash', ?, ?, ?)",
        (data.user_id, f"Crash {crash_multiplier}x", data.bet, payout if won else 0)
    )
    conn.commit()
    conn.close()

    return {
        "success": True,
        "crashed_at": crash_multiplier,
        "won": won,
        "payout": payout,
        "new_balance": new_balance
    }

app.mount("/", StaticFiles(directory=".", html=True), name="static")
