"""FastAPI service for StayScout's SQLite-backed travel and booking flow."""
from __future__ import annotations

import csv
import sqlite3
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import geoapify_api_key
from .geoapify import GeoapifyRequestError, GeoapifyRateLimitError, MissingGeoapifyKeyError, ZipNotFoundError, lookup_us_zip, search_hotels
from .models import ExternalHotel
from .chat import ChatError, answer_question

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "stayscout.db"
DEMO_STAY_DATES = tuple(f"2026-10-{day:02d}" for day in range(10, 15))

app = FastAPI(title="StayScout API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)


class BookingCreate(BaseModel):
    user_id: str
    trip_id: str


class ChatQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=1200)


@app.post("/api/chat")
def hotel_chat(payload: ChatQuestion) -> dict[str, object]:
    """Generate SQL, check local retrieval, then request a grounded LLM answer."""
    try:
        return answer_question(DATABASE_PATH, payload.question)
    except ChatError as error:
        headers = {"Retry-After": "60"} if error.status == 429 else None
        raise HTTPException(status_code=error.status, detail=str(error), headers=headers) from None


class BookingStatusUpdate(BaseModel):
    status: Literal["confirmed", "cancelled"]


class LocalSearchCenter(BaseModel):
    postcode: str = Field(pattern=r"^[0-9]{5}$")
    country_code: Literal["us"]
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    locality: str | None = None


class LocalHotelSave(BaseModel):
    hotel: ExternalHotel
    zip_code: str
    center: LocalSearchCenter


def read_csv(filename: str) -> list[dict[str, str]]:
    """Read one instructor CSV. utf-8-sig removes Excel's optional byte-order mark."""
    path = DATA_DIR / filename
    if not path.exists():
        raise RuntimeError(f"Required data file is missing: {filename}")
    with path.open(newline="", encoding="utf-8-sig") as data_file:
        return list(csv.DictReader(data_file))


def connect() -> sqlite3.Connection:
    """Open a SQLite connection configured for dictionary-like rows and foreign keys."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database() -> None:
    """Create the schema and seed it exactly once from the supplied CSVs."""
    connection = connect()
    try:
        with connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS app_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS hotels (
                    hotel_id TEXT PRIMARY KEY,
                    hotel_name TEXT NOT NULL,
                    city TEXT NOT NULL,
                    state TEXT NOT NULL,
                    nightly_rate_usd REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS trips (
                    trip_id TEXT PRIMARY KEY,
                    hotel_id TEXT NOT NULL REFERENCES hotels(hotel_id),
                    trip_name TEXT NOT NULL,
                    check_in TEXT NOT NULL,
                    check_out TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS bookings (
                    booking_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL REFERENCES users(user_id),
                    trip_id TEXT NOT NULL REFERENCES trips(trip_id),
                    booked_on TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('confirmed', 'cancelled'))
                );
                CREATE TABLE IF NOT EXISTS saved_hotels (
                    hotel_id TEXT PRIMARY KEY CHECK(length(trim(hotel_id)) > 0),
                    name TEXT,
                    address TEXT,
                    latitude REAL NOT NULL CHECK(latitude >= -90 AND latitude <= 90),
                    longitude REAL NOT NULL CHECK(longitude >= -180 AND longitude <= 180)
                );
                CREATE TABLE IF NOT EXISTS saved_hotel_searches (
                    hotel_id TEXT NOT NULL REFERENCES saved_hotels(hotel_id) ON DELETE CASCADE,
                    zip_code TEXT NOT NULL CHECK(length(zip_code) = 5 AND zip_code GLOB '[0-9][0-9][0-9][0-9][0-9]'),
                    country_code TEXT NOT NULL CHECK(country_code = 'us'),
                    center_latitude REAL NOT NULL CHECK(center_latitude >= -90 AND center_latitude <= 90),
                    center_longitude REAL NOT NULL CHECK(center_longitude >= -180 AND center_longitude <= 180),
                    locality TEXT,
                    PRIMARY KEY (hotel_id, zip_code)
                );
                CREATE TABLE IF NOT EXISTS demo_hotel_nights (
                    hotel_id TEXT NOT NULL REFERENCES saved_hotels(hotel_id) ON DELETE CASCADE,
                    stay_date TEXT NOT NULL CHECK(length(stay_date) = 10 AND date(stay_date) IS NOT NULL AND date(stay_date) = stay_date),
                    nightly_rate_cents INTEGER NOT NULL DEFAULT 10000 CHECK(nightly_rate_cents >= 0),
                    rooms_available INTEGER NOT NULL DEFAULT 20 CHECK(rooms_available >= 0),
                    PRIMARY KEY (hotel_id, stay_date)
                );
                """
            )
            already_seeded = connection.execute(
                "SELECT 1 FROM app_metadata WHERE key = 'initial_csv_seeded'"
            ).fetchone()
            if already_seeded:
                return

            connection.executemany(
                "INSERT INTO hotels VALUES (:hotel_id, :hotel_name, :city, :state, :nightly_rate_usd)",
                read_csv("hotels.csv"),
            )
            connection.executemany(
                "INSERT INTO trips VALUES (:trip_id, :hotel_id, :trip_name, :check_in, :check_out)",
                read_csv("trips.csv"),
            )
            connection.executemany(
                "INSERT INTO users VALUES (:user_id, :display_name)",
                read_csv("users.csv"),
            )
            connection.executemany(
                "INSERT INTO bookings VALUES (:booking_id, :user_id, :trip_id, :booked_on, :status)",
                read_csv("bookings.csv"),
            )
            connection.execute("INSERT INTO app_metadata VALUES ('initial_csv_seeded', 'true')")
    finally:
        connection.close()


def format_money(amount: Decimal) -> str:
    return f"${amount:,.2f}"


def stay_from_row(row: sqlite3.Row) -> dict[str, str]:
    check_in = date.fromisoformat(row["check_in"])
    check_out = date.fromisoformat(row["check_out"])
    nights = (check_out - check_in).days
    nightly_rate = Decimal(str(row["nightly_rate_usd"]))
    return {
        "trip_id": row["trip_id"],
        "trip_name": row["trip_name"],
        "hotel_name": row["hotel_name"],
        "city": row["city"],
        "state": row["state"],
        "check_in": row["check_in"],
        "check_out": row["check_out"],
        "nights": str(nights),
        "nightly_rate": format_money(nightly_rate),
        "stay_price": format_money(nightly_rate * nights),
    }


def stay_query() -> str:
    return """
        SELECT trips.trip_id, trips.trip_name, trips.check_in, trips.check_out,
               hotels.hotel_name, hotels.city, hotels.state, hotels.nightly_rate_usd
        FROM trips JOIN hotels ON trips.hotel_id = hotels.hotel_id
    """


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "database": str(DATABASE_PATH),
        "geoapify": "key is configured" if geoapify_api_key() else "key is not configured",
    }


def location_for_api(zip_code: str) -> dict[str, object]:
    """Translate controller outcomes to credential-safe HTTP responses."""
    try:
        return lookup_us_zip(zip_code)
    except MissingGeoapifyKeyError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except ZipNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except GeoapifyRateLimitError as error:
        raise HTTPException(status_code=429, detail=str(error), headers={"Retry-After": "60"}) from error
    except GeoapifyRequestError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


def normalized_zip(zip_code: str) -> str:
    value = zip_code.strip()
    if len(value) != 5 or not value.isascii() or not value.isdigit():
        raise HTTPException(status_code=422, detail="Enter a five-digit U.S. ZIP code.")
    return value


def local_result(zip_code: str) -> dict[str, object]:
    """Read only the saved subset for an exact ZIP; do not call Geoapify here."""
    connection = connect()
    try:
        rows = connection.execute(
            """
            SELECT saved_hotels.hotel_id, saved_hotels.name, saved_hotels.address,
                   saved_hotels.latitude, saved_hotels.longitude,
                   saved_hotel_searches.country_code, saved_hotel_searches.center_latitude,
                   saved_hotel_searches.center_longitude, saved_hotel_searches.locality,
                   demo_hotel_nights.stay_date, demo_hotel_nights.nightly_rate_cents,
                   demo_hotel_nights.rooms_available
            FROM saved_hotel_searches
            JOIN saved_hotels ON saved_hotels.hotel_id = saved_hotel_searches.hotel_id
            LEFT JOIN demo_hotel_nights ON demo_hotel_nights.hotel_id = saved_hotels.hotel_id
            WHERE saved_hotel_searches.zip_code = ?
            ORDER BY saved_hotels.name COLLATE NOCASE, saved_hotels.hotel_id, demo_hotel_nights.stay_date
            """,
            (zip_code,),
        ).fetchall()
    except sqlite3.Error as error:
        raise HTTPException(status_code=500, detail="Local hotel storage could not be read. Please try again.") from error
    finally:
        connection.close()

    if not rows:
        return {"source": "local", "zip_code": zip_code, "count": 0, "hotels": []}

    first = rows[0]
    center = {
        "postcode": zip_code,
        "country_code": first["country_code"],
        "latitude": first["center_latitude"],
        "longitude": first["center_longitude"],
        "locality": first["locality"],
    }
    hotels: dict[str, dict[str, object]] = {}
    for row in rows:
        hotel_id = row["hotel_id"]
        if hotel_id not in hotels:
            hotels[hotel_id] = {
                "provider": "geoapify",
                "place_id": hotel_id,
                "name": row["name"],
                "address": row["address"],
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "distance_meters": 0,
                "saved_locally": True,
                "demo_nights": [],
            }
        if row["stay_date"] is not None:
            hotels[hotel_id]["demo_nights"].append(
                {
                    "stay_date": row["stay_date"],
                    "nightly_rate_cents": row["nightly_rate_cents"],
                    "rooms_available": row["rooms_available"],
                }
            )
    return {
        "source": "local",
        "center": center,
        "hotels": list(hotels.values()),
        "count": len(hotels),
        "radius_meters": 5000,
        "observed_at": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/demo/zip-location")
def demo_zip_location() -> dict[str, object]:
    """The fixed ZIP 16802 route used by the in-class demonstration."""
    return location_for_api("16802")


@app.get("/api/zip-location")
def zip_location(zip_code: str = Query(..., pattern=r"^[0-9]{5}$", description="Five-digit U.S. ZIP code")) -> dict[str, object]:
    """Look up a user-entered five-digit U.S. ZIP code."""
    return location_for_api(zip_code)


@app.get("/api/hotels")
def hotels_near_zip(zip_code: str = Query(..., pattern=r"^[0-9]{5}$")) -> dict[str, object]:
    """Discover hotel locations; this endpoint never promises bookable rooms."""
    try:
        return search_hotels(zip_code)
    except MissingGeoapifyKeyError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except ZipNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except GeoapifyRateLimitError as error:
        raise HTTPException(status_code=429, detail=str(error), headers={"Retry-After": "60"}) from error
    except GeoapifyRequestError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


@app.get("/api/local-hotels")
def saved_hotels_for_zip(zip_code: str = Query(..., pattern=r"^[0-9]{5}$")) -> dict[str, object]:
    """Return only the local saved subset for the requested ZIP."""
    return local_result(normalized_zip(zip_code))


@app.post("/api/local-hotels", status_code=201)
def save_local_hotel(payload: LocalHotelSave) -> dict[str, object]:
    """Save a returned place once, with five non-destructive classroom nights."""
    zip_code = normalized_zip(payload.zip_code)
    if payload.center.postcode != zip_code:
        raise HTTPException(status_code=422, detail="The saved hotel must use the current searched ZIP location.")

    hotel = payload.hotel
    if not hotel.place_id.strip():
        raise HTTPException(status_code=422, detail="A provider hotel identifier is required.")
    connection = connect()
    try:
        with connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO saved_hotels (hotel_id, name, address, latitude, longitude)
                VALUES (?, ?, ?, ?, ?)
                """,
                (hotel.place_id, hotel.name, hotel.address, hotel.latitude, hotel.longitude),
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO saved_hotel_searches
                (hotel_id, zip_code, country_code, center_latitude, center_longitude, locality)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    hotel.place_id,
                    zip_code,
                    payload.center.country_code,
                    payload.center.latitude,
                    payload.center.longitude,
                    payload.center.locality,
                ),
            )
            connection.executemany(
                "INSERT OR IGNORE INTO demo_hotel_nights (hotel_id, stay_date) VALUES (?, ?)",
                [(hotel.place_id, stay_date) for stay_date in DEMO_STAY_DATES],
            )
        return {
            "hotel_id": hotel.place_id,
            "saved": True,
            "message": "Hotel saved locally with five simulated nightly records.",
        }
    except sqlite3.Error as error:
        raise HTTPException(status_code=500, detail="Local hotel storage could not save this hotel. Please try again.") from error
    finally:
        connection.close()


@app.delete("/api/local-hotels/{hotel_id}")
def remove_local_hotel(hotel_id: str) -> dict[str, str]:
    """Delete one saved hotel and its dependent classroom records atomically."""
    if not hotel_id.strip():
        raise HTTPException(status_code=422, detail="A saved hotel identifier is required.")
    connection = connect()
    try:
        with connection:
            result = connection.execute("DELETE FROM saved_hotels WHERE hotel_id = ?", (hotel_id,))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Saved hotel not found.")
        return {"hotel_id": hotel_id, "message": "Hotel and its local classroom records were removed."}
    except sqlite3.Error as error:
        raise HTTPException(status_code=500, detail="Local hotel storage could not remove this hotel. Please try again.") from error
    finally:
        connection.close()


@app.get("/api/stays")
def search_stays(query: str = Query(..., min_length=1, description="Hotel name to search")) -> dict[str, object]:
    """Search SQLite hotel names and return their joined available trips."""
    search_text = query.strip()
    if not search_text:
        raise HTTPException(status_code=422, detail="Enter a hotel name to search.")
    connection = connect()
    try:
        rows = connection.execute(
            stay_query() + " WHERE LOWER(hotels.hotel_name) LIKE ? ORDER BY trips.check_in, trips.trip_id",
            (f"%{search_text.casefold()}%",),
        ).fetchall()
        return {"query": search_text, "count": len(rows), "stays": [stay_from_row(row) for row in rows]}
    finally:
        connection.close()


@app.get("/api/users")
def list_users() -> list[dict[str, str]]:
    connection = connect()
    try:
        return [dict(row) for row in connection.execute("SELECT user_id, display_name FROM users ORDER BY user_id")]
    finally:
        connection.close()


@app.post("/api/bookings", status_code=201)
def create_booking(booking: BookingCreate) -> dict[str, str]:
    """Create a new simulated booking with a unique identifier."""
    connection = connect()
    try:
        user_exists = connection.execute("SELECT 1 FROM users WHERE user_id = ?", (booking.user_id,)).fetchone()
        trip_exists = connection.execute("SELECT 1 FROM trips WHERE trip_id = ?", (booking.trip_id,)).fetchone()
        if not user_exists or not trip_exists:
            raise HTTPException(status_code=404, detail="Choose a valid traveler and stay.")
        booking_id = f"B{uuid4().hex[:8].upper()}"
        with connection:
            connection.execute(
                "INSERT INTO bookings VALUES (?, ?, ?, ?, 'confirmed')",
                (booking_id, booking.user_id, booking.trip_id, date.today().isoformat()),
            )
        return {"booking_id": booking_id, "message": "Booking created and confirmed."}
    finally:
        connection.close()


@app.get("/api/bookings")
def booking_history(user_id: str = Query(..., min_length=1)) -> list[dict[str, str]]:
    """Return a traveler's history from SQLite, including cancelled records."""
    connection = connect()
    try:
        rows = connection.execute(
            """
            SELECT bookings.booking_id, bookings.booked_on, bookings.status,
                   users.display_name, trips.trip_id, trips.trip_name, trips.check_in, trips.check_out,
                   hotels.hotel_name, hotels.city, hotels.state, hotels.nightly_rate_usd
            FROM bookings
            JOIN users ON bookings.user_id = users.user_id
            JOIN trips ON bookings.trip_id = trips.trip_id
            JOIN hotels ON trips.hotel_id = hotels.hotel_id
            WHERE bookings.user_id = ?
            ORDER BY bookings.booked_on DESC, bookings.booking_id DESC
            """,
            (user_id,),
        ).fetchall()
        return [
            {
                **{key: value for key, value in dict(row).items() if key != "nightly_rate_usd"},
                **stay_from_row(row),
            }
            for row in rows
        ]
    finally:
        connection.close()


@app.patch("/api/bookings/{booking_id}")
def update_booking(booking_id: str, update: BookingStatusUpdate) -> dict[str, str]:
    connection = connect()
    try:
        with connection:
            result = connection.execute(
                "UPDATE bookings SET status = ? WHERE booking_id = ?", (update.status, booking_id)
            )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Booking not found.")
        return {"booking_id": booking_id, "status": update.status}
    finally:
        connection.close()


@app.delete("/api/bookings/{booking_id}")
def delete_booking(booking_id: str) -> dict[str, str]:
    connection = connect()
    try:
        with connection:
            result = connection.execute("DELETE FROM bookings WHERE booking_id = ?", (booking_id,))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Booking not found.")
        return {"message": "Booking deleted."}
    finally:
        connection.close()
