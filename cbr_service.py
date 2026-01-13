# cbr_service.py
import sqlite3
from datetime import datetime


def get_db_connection():
    """Вспомогательная функция для получения соединения с БД."""
    conn = sqlite3.connect("cbr_rates.db")
    conn.row_factory = sqlite3.Row  # опционально, для удобства
    return conn


def init_db():
    """Инициализация базы данных."""
    try:
        with get_db_connection() as conn:
            conn.execute(
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
    except sqlite3.Error as e:
        print(f"Ошибка инициализации БД: {e}")


def save_to_db(date: str, rates: dict):
    """Сохраняет курсы валют в БД."""
    try:
        with get_db_connection() as conn:
            for code, rate in rates.items():
                conn.execute(
                    """
                    INSERT OR REPLACE INTO currency_rates (date, currency_code, rate)
                    VALUES (?, ?, ?)
                    """,
                    (date, code, rate),
                )
    except sqlite3.Error as e:
        print(f"Ошибка сохранения в БД: {e}")
        raise


def get_rates_for_date(date: str):
    """
    Возвращает курсы за дату из БД.
    Предполагается, что дата уже валидна (проверена в API).
    """
    try:
        with get_db_connection() as conn:
            cur = conn.execute(
                "SELECT currency_code, rate FROM currency_rates WHERE date = ?",
                (date,),
            )
            rows = cur.fetchall()
            if not rows:
                return None
            return {row[0]: row[1] for row in rows}
    except sqlite3.Error as e:
        print(f"Ошибка чтения из БД: {e}")
        return None


def get_history(limit: int = 50):
    """Возвращает историю запросов."""
    try:
        with get_db_connection() as conn:
            cur = conn.execute(
                """
                SELECT date, currency_code, rate, created_at
                FROM currency_rates
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cur.fetchall()
            return [
                {"date": r[0], "currency": r[1], "rate": r[2], "saved_at": r[3]}
                for r in rows
            ]
    except sqlite3.Error as e:
        print(f"Ошибка получения истории: {e}")
        return []


# Инициализация при импорте
init_db()
