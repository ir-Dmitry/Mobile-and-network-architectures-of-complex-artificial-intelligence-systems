# cbr_service.py
import sqlite3
from datetime import datetime


def init_db():
    conn = sqlite3.connect("cbr_rates.db")
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS currency_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            currency_code TEXT NOT NULL,
            rate REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, currency_code)
        )
        """
    )
    conn.commit()
    conn.close()


def save_to_db(date: str, rates: dict):
    conn = sqlite3.connect("cbr_rates.db")
    cur = conn.cursor()
    for code, rate in rates.items():
        cur.execute(
            """
            INSERT OR REPLACE INTO currency_rates (date, currency_code, rate)
            VALUES (?, ?, ?)
            """,
            (date, code, rate),
        )
    conn.commit()
    conn.close()


def get_rates_for_date(date: str):
    # Валидация формата даты
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return None

    conn = sqlite3.connect("cbr_rates.db")
    cur = conn.cursor()
    cur.execute(
        "SELECT currency_code, rate FROM currency_rates WHERE date = ?", (date,)
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return None
    return {row[0]: row[1] for row in rows}


def get_history(limit: int = 50):
    conn = sqlite3.connect("cbr_rates.db")
    cur = conn.cursor()
    cur.execute(
        """
        SELECT date, currency_code, rate, created_at
        FROM currency_rates
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {"date": r[0], "currency": r[1], "rate": r[2], "saved_at": r[3]} for r in rows
    ]


init_db()
