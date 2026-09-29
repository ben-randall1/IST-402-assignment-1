"""Mocked contract checks for the Geoapify ZIP lookup controller."""
from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

import httpx

from backend.geoapify import GeoapifyRequestError, ZipNotFoundError, lookup_us_zip


class GeoapifyZipLookupTests(unittest.TestCase):
    @patch("backend.geoapify.geoapify_api_key", return_value="test-key")
    @patch("backend.geoapify.httpx.get")
    def test_returns_a_small_verified_location_response(self, get, _key):
        response = Mock()
        response.json.return_value = {
            "results": [
                {
                    "postcode": "16802",
                    "country_code": "us",
                    "lat": 40.7934,
                    "lon": -77.8600,
                    "city": "University Park",
                    "apiKey": "must-not-return",
                }
            ]
        }
        get.return_value = response

        location = lookup_us_zip("16802")

        self.assertEqual(
            location,
            {
                "postcode": "16802",
                "country_code": "us",
                "latitude": 40.7934,
                "longitude": -77.86,
                "locality": "University Park",
            },
        )
        get.assert_called_once()
        self.assertEqual(get.call_args.kwargs["params"]["postcode"], "16802")
        self.assertEqual(get.call_args.kwargs["params"]["type"], "postcode")
        self.assertEqual(get.call_args.kwargs["params"]["filter"], "countrycode:us")
        self.assertEqual(get.call_args.kwargs["params"]["format"], "json")

    @patch("backend.geoapify.geoapify_api_key", return_value="test-key")
    @patch("backend.geoapify.httpx.get")
    def test_rejects_a_mismatched_result(self, get, _key):
        response = Mock()
        response.json.return_value = {
            "results": [
                {"postcode": "16801", "country_code": "us", "lat": 40.79, "lon": -77.86}
            ]
        }
        get.return_value = response

        with self.assertRaises(ZipNotFoundError):
            lookup_us_zip("16802")

    @patch("backend.geoapify.geoapify_api_key", return_value="test-key")
    @patch("backend.geoapify.httpx.get", side_effect=httpx.TimeoutException("timeout"))
    def test_sanitizes_provider_failures(self, _get, _key):
        with self.assertRaisesRegex(GeoapifyRequestError, "location service is unavailable"):
            lookup_us_zip("16802")


if __name__ == "__main__":
    unittest.main()
