"""FastAPI service for city-based hotel-stay searches."""
from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

app = FastAPI(title="StayScout API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def read_csv(filename: str) -> list[dict[str, str]]:
    """Read a project data CSV and return its rows as string dictionaries."""
    path = DATA_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=500, detail=f"Required data file is missing: {filename}")
    # The instructor CSVs use a UTF-8 BOM so they open correctly in Excel.
    with path.open(newline="", encoding="utf-8-sig") as data_file:
        return list(csv.DictReader(data_file))


def value(row: dict[str, str], *names: str) -> str:
    """Read the first available spelling to tolerate common travel-data headers."""
    for name in names:
        if row.get(name):
            return row[name]
    return ""


def format_money(amount: Decimal) -> str:
    """Format a CSV currency value without floating-point rounding errors."""
    return f"${amount:,.2f}"


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/stays")
def search_stays(city: str = Query(..., min_length=1, description="City to search")) -> dict[str, object]:
    """Join trips to hotels and return stays whose hotel city matches the query."""
    normalized_city = city.strip().casefold()
    if not normalized_city:
        raise HTTPException(status_code=422, detail="City must contain text.")

    hotels_by_id = {value(hotel, "hotel_id", "id"): hotel for hotel in read_csv("hotels.csv")}
    stays: list[dict[str, str]] = []
    for trip in read_csv("trips.csv"):
        hotel = hotels_by_id.get(value(trip, "hotel_id"))
        if hotel is None:
            continue
        hotel_city = value(hotel, "city")
        if hotel_city.casefold() != normalized_city:
            continue
        check_in = value(trip, "check_in", "start_date", "date_start")
        check_out = value(trip, "check_out", "end_date", "date_end")
        try:
            nights = (date.fromisoformat(check_out) - date.fromisoformat(check_in)).days
            nightly_rate = Decimal(value(hotel, "nightly_rate_usd", "nightly_rate", "price"))
        except (InvalidOperation, ValueError):
            raise HTTPException(status_code=500, detail="A trip has an invalid date or nightly rate.")
        stays.append(
            {
                "trip_id": value(trip, "trip_id", "id"),
                "trip_name": value(trip, "trip_name"),
                "hotel_name": value(hotel, "hotel_name", "name"),
                "city": hotel_city,
                "state": value(hotel, "state"),
                "check_in": check_in,
                "check_out": check_out,
                "nights": str(nights),
                "nightly_rate": format_money(nightly_rate),
                "stay_price": format_money(nightly_rate * nights),
            }
        )
    return {"city": city.strip(), "count": len(stays), "stays": stays}
