"""Local hotel storage checks use isolated SQLite files and never call Geoapify."""
from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app


def hotel_payload(hotel_id: str = "provider-hotel-1", zip_code: str = "16802") -> dict:
    return {
        "hotel": {
            "provider": "geoapify",
            "place_id": hotel_id,
            "name": "Saved Fixture Hotel",
            "address": "1 Fixture Way, State College, PA",
            "latitude": 40.801,
            "longitude": -77.86,
            "distance_meters": 500,
        },
        "zip_code": zip_code,
        "center": {
            "postcode": zip_code,
            "country_code": "us",
            "latitude": 40.803,
            "longitude": -77.861,
            "locality": "State College",
        },
    }


class LocalHotelStorageTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.database = Path(self.directory.name) / "local-hotels.db"
        self.database_patch = patch("backend.main.DATABASE_PATH", self.database)
        self.database_patch.start()
        self.client_context = TestClient(app)
        self.client = self.client_context.__enter__()

    def tearDown(self):
        self.client_context.__exit__(None, None, None)
        self.database_patch.stop()
        self.directory.cleanup()

    def rows(self, query: str, parameters: tuple = ()) -> list[tuple]:
        with sqlite3.connect(self.database) as connection:
            return connection.execute(query, parameters).fetchall()

    def test_migration_is_additive_and_keeps_assignment_one_seed_records(self):
        table_names = {row[0] for row in self.rows("SELECT name FROM sqlite_master WHERE type = 'table'")}
        self.assertTrue({"hotels", "trips", "users", "bookings", "saved_hotels", "saved_hotel_searches", "demo_hotel_nights"} <= table_names)
        self.assertGreater(self.rows("SELECT COUNT(*) FROM hotels")[0][0], 0)
        self.assertGreater(self.rows("SELECT COUNT(*) FROM trips")[0][0], 0)
        night_columns = {row[1]: row for row in self.rows("PRAGMA table_info(demo_hotel_nights)")}
        self.assertIn("10000", night_columns["nightly_rate_cents"][4])
        self.assertIn("20", night_columns["rooms_available"][4])

    def test_save_creates_one_hotel_zip_association_and_five_default_nights(self):
        response = self.client.post("/api/local-hotels", json=hotel_payload())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.rows("SELECT hotel_id, name FROM saved_hotels"), [("provider-hotel-1", "Saved Fixture Hotel")])
        self.assertEqual(self.rows("SELECT hotel_id, zip_code FROM saved_hotel_searches"), [("provider-hotel-1", "16802")])
        self.assertEqual(
            self.rows("SELECT stay_date, nightly_rate_cents, rooms_available FROM demo_hotel_nights ORDER BY stay_date"),
            [(f"2026-10-{day:02d}", 10000, 20) for day in range(10, 15)],
        )

    def test_repeated_save_never_duplicates_or_overwrites_edited_nights(self):
        self.assertEqual(self.client.post("/api/local-hotels", json=hotel_payload()).status_code, 201)
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "UPDATE demo_hotel_nights SET nightly_rate_cents = 500, rooms_available = 10 WHERE hotel_id = ? AND stay_date = ?",
                ("provider-hotel-1", "2026-10-10"),
            )
        self.assertEqual(self.client.post("/api/local-hotels", json=hotel_payload()).status_code, 201)
        self.assertEqual(self.rows("SELECT COUNT(*) FROM saved_hotels")[0][0], 1)
        self.assertEqual(self.rows("SELECT COUNT(*) FROM saved_hotel_searches")[0][0], 1)
        self.assertEqual(self.rows("SELECT COUNT(*) FROM demo_hotel_nights")[0][0], 5)
        self.assertEqual(
            self.rows("SELECT nightly_rate_cents, rooms_available FROM demo_hotel_nights WHERE stay_date = '2026-10-10'"),
            [(500, 10)],
        )

    def test_local_lookup_returns_stored_context_and_committed_values(self):
        self.client.post("/api/local-hotels", json=hotel_payload())
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "UPDATE demo_hotel_nights SET nightly_rate_cents = 600, rooms_available = 7 WHERE hotel_id = ? AND stay_date = ?",
                ("provider-hotel-1", "2026-10-12"),
            )
        result = self.client.get("/api/local-hotels?zip_code=16802")
        self.assertEqual(result.status_code, 200)
        body = result.json()
        self.assertEqual(body["source"], "local")
        self.assertEqual(body["center"]["locality"], "State College")
        self.assertTrue(body["hotels"][0]["saved_locally"])
        october_twelve = next(night for night in body["hotels"][0]["demo_nights"] if night["stay_date"] == "2026-10-12")
        self.assertEqual(october_twelve, {"stay_date": "2026-10-12", "nightly_rate_cents": 600, "rooms_available": 7})

    def test_empty_local_lookup_is_successful_and_does_not_create_data(self):
        result = self.client.get("/api/local-hotels?zip_code=16802")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json(), {"source": "local", "zip_code": "16802", "count": 0, "hotels": []})

    def test_remove_cascades_dependents_and_preserves_another_saved_hotel(self):
        self.client.post("/api/local-hotels", json=hotel_payload("provider-hotel-1"))
        self.client.post("/api/local-hotels", json=hotel_payload("provider-hotel-2"))
        removed = self.client.delete("/api/local-hotels/provider-hotel-1")
        self.assertEqual(removed.status_code, 200)
        self.assertEqual(self.rows("SELECT hotel_id FROM saved_hotels ORDER BY hotel_id"), [("provider-hotel-2",)])
        self.assertEqual(self.rows("SELECT hotel_id FROM saved_hotel_searches ORDER BY hotel_id"), [("provider-hotel-2",)])
        self.assertEqual(self.rows("SELECT DISTINCT hotel_id FROM demo_hotel_nights"), [("provider-hotel-2",)])
        self.assertEqual(self.client.delete("/api/local-hotels/provider-hotel-1").status_code, 404)

    def test_schema_rejects_invalid_stay_date_and_negative_classroom_values(self):
        self.client.post("/api/local-hotels", json=hotel_payload())
        with sqlite3.connect(self.database) as connection:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO demo_hotel_nights (hotel_id, stay_date) VALUES (?, ?)",
                    ("provider-hotel-1", "2026-99-99"),
                )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "UPDATE demo_hotel_nights SET rooms_available = -1 WHERE hotel_id = ?",
                    ("provider-hotel-1",),
                )

    def test_bad_local_payload_is_rejected_without_writing(self):
        invalid = hotel_payload()
        invalid["center"]["postcode"] = "02108"
        self.assertEqual(self.client.post("/api/local-hotels", json=invalid).status_code, 422)
        invalid = hotel_payload()
        invalid["hotel"]["place_id"] = "   "
        self.assertEqual(self.client.post("/api/local-hotels", json=invalid).status_code, 422)
        self.assertEqual(self.rows("SELECT COUNT(*) FROM saved_hotels")[0][0], 0)


if __name__ == "__main__":
    unittest.main()
