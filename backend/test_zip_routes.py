"""Mocked route checks for the public ZIP lookup endpoints."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.geoapify import MissingGeoapifyKeyError
from backend.main import app


class ZipRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("backend.main.lookup_us_zip")
    def test_demo_route_returns_the_controller_response(self, lookup):
        lookup.return_value = {
            "postcode": "16802",
            "country_code": "us",
            "latitude": 40.79,
            "longitude": -77.86,
            "locality": "University Park",
        }

        response = self.client.get("/api/demo/zip-location")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["postcode"], "16802")
        lookup.assert_called_once_with("16802")

    @patch("backend.main.lookup_us_zip", side_effect=MissingGeoapifyKeyError("Geoapify API key is not configured."))
    def test_demo_route_returns_a_safe_missing_key_error(self, _lookup):
        response = self.client.get("/api/demo/zip-location")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "Geoapify API key is not configured."})

    @patch("backend.main.lookup_us_zip")
    def test_entered_zip_route_forwards_the_value(self, lookup):
        lookup.return_value = {
            "postcode": "00501",
            "country_code": "us",
            "latitude": 40.9223,
            "longitude": -72.6371,
            "locality": "Holtsville",
        }

        response = self.client.get("/api/zip-location?zip_code=00501")

        self.assertEqual(response.status_code, 200)
        lookup.assert_called_once_with("00501")


if __name__ == "__main__":
    unittest.main()
