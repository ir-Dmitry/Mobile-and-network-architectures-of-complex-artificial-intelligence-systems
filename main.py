# main.py
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional
from cbr_service import get_rates_for_date, get_history

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.get("/api/rates")
async def api_rates(date: str = Query(..., regex=r"^\d{4}-\d{2}-\d{2}$")):
    rates = get_rates_for_date(date)
    if rates is None:
        return {"error": "Не удалось получить данные от ЦБ РФ"}
    return {"date": date, "rates": rates}


@app.get("/api/history")
async def api_history(limit: Optional[int] = 50):
    records = get_history(limit)
    return {"history": records}
