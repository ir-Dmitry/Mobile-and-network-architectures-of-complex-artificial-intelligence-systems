# cbr_service.py
import requests
import xml.etree.ElementTree as ET
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


def fetch_from_cbr(date_str: str):
    url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={date_str}"
    try:
        resp = requests.get(url)
        resp.encoding = "windows-1251"
        root = ET.fromstring(resp.text)
        rates = {}
        for v in root.findall("Valute"):
            code = v.find("CharCode").text
            nominal = int(v.find("Nominal").text)
            value = float(v.find("Value").text.replace(",", "."))
            rates[code] = round(value / nominal, 6)
        return rates
    except:
        return None


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
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        date_api = dt.strftime("%d/%m/%Y")
    except:
        return None

    rates = fetch_from_cbr(date_api)
    if rates is not None:
        save_to_db(date, rates)
    return rates


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
