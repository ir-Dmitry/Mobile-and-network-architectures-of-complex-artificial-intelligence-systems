# main.py
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional, Dict
from pydantic import BaseModel
from datetime import datetime
from cbr_service import get_rates_for_date, get_history, save_to_db

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


class IngestPayload(BaseModel):
    date: str
    rates: Dict[str, float]


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.get("/api/rates")
async def api_rates(date: str = Query(..., regex=r"^\d{4}-\d{2}-\d{2}$")):
    rates = get_rates_for_date(date)
    if rates is None:
        return {"date": date, "rates": None}
    return {"date": date, "rates": rates}


@app.get("/api/history")
async def api_history(limit: Optional[int] = 50):
    records = get_history(limit)
    return {"history": records}


@app.post("/api/ingest")
async def ingest_from_function(payload: IngestPayload):
    # Валидация формата даты
    try:
        datetime.strptime(payload.date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Неверный формат даты. Используйте YYYY-MM-DD"
        )

    save_to_db(payload.date, payload.rates)
    return {"status": "ok", "saved": len(payload.rates)}
