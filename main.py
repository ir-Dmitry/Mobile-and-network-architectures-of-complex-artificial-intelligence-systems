# main.py
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional, Dict
from pydantic import BaseModel
from datetime import datetime
from cbr_service import get_rates_for_date, get_history, save_to_db

app = FastAPI(
    title="Currency Rates API",
    description="API для получения курсов валют ЦБ РФ через облачную функцию",
)

app.mount("/static", StaticFiles(directory="static"), name="static")


class IngestPayload(BaseModel):
    """Модель данных для приёма курсов от облачной функции."""

    date: str
    rates: Dict[str, float]


@app.get("/")
async def root():
    """Основная страница интерфейса."""
    return FileResponse("static/index.html")


@app.get("/api/rates")
async def api_rates(date: str = Query(..., regex=r"^\d{4}-\d{2}-\d{2}$")):
    """
    Возвращает курсы валют за указанную дату.
    Если данных нет в БД — возвращает rates: null (не ошибка).
    """
    rates = get_rates_for_date(date)
    if rates is None:
        return {"date": date, "rates": None}
    return {"date": date, "rates": rates}


@app.get("/api/history")
async def api_history(limit: Optional[int] = 50):
    """Возвращает историю сохранённых курсов."""
    records = get_history(limit)
    return {"history": records}


@app.post("/api/ingest")
async def ingest_from_function(payload: IngestPayload):
    """
    Принимает курсы от облачной функции и сохраняет в БД.
    Вызывается только из Yandex Cloud Function.
    """
    try:
        datetime.strptime(payload.date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Неверный формат даты. Используйте YYYY-MM-DD"
        )

    save_to_db(payload.date, payload.rates)
    return {"status": "ok", "saved": len(payload.rates)}
