"""FastAPI service for city-based hotel-stay searches."""
from __future__ import annotations

import csv
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
    with path.open(newline="", encoding="utf-8") as data_file:
        return list(csv.DictReader(data_file))


def value(row: dict[str, str], *names: str) -> str:
    """Read the first available spelling to tolerate common travel-data headers."""
    for name in names:
        if row.get(name):
            return row[name]
    return ""


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
        stays.append(
            {
                "trip_id": value(trip, "trip_id", "id"),
                "hotel_name": value(hotel, "hotel_name", "name"),
                "city": hotel_city,
                "country": value(hotel, "country"),
                "check_in": value(trip, "check_in", "start_date", "date_start"),
                "check_out": value(trip, "check_out", "end_date", "date_end"),
                "price": value(trip, "price", "price_per_night", "nightly_rate"),
            }
        )
    return {"city": city.strip(), "count": len(stays), "stays": stays}
