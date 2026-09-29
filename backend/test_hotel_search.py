"""Repeatable provider contracts and legacy regressions; no live API calls."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

from backend.main import app
from backend.geoapify import GEOCODING_URL, PLACES_URL, GeoapifyRequestError, ZipNotFoundError, lookup_us_zip, search_hotels

CENTER = {"postcode": "02108", "country_code": "us", "lat": 42.357, "lon": -71.063, "city": "Boston", "result_type": "postcode"}
FEATURE = {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-71.064, 42.358]}, "properties": {"place_id": "fixed-hotel-1", "name": "Fixture Hotel", "formatted": "Fixture address, Boston", "lat": 42.358, "lon": -71.064}}

def response(url, data, status=200):
    return httpx.Response(status, json=data, request=httpx.Request("GET", url))


@patch("backend.geoapify.geoapify_api_key", return_value="test-secret-must-not-leak")
class HotelSearchTests(unittest.TestCase):
    def mock_search(self, features):
        return patch("backend.geoapify.httpx.get", side_effect=[response(GEOCODING_URL, {"results": [CENTER]}), response(PLACES_URL, {"features": features})])

    def test_search_preserves_leading_zero_and_uses_exact_radius(self, _key):
        with self.mock_search([FEATURE]) as get:
            data = search_hotels("02108")
        self.assertEqual(data["center"]["postcode"], "02108")
        self.assertEqual(get.call_args_list[0].kwargs["params"]["postcode"], "02108")
        params = get.call_args_list[1].kwargs["params"]
        self.assertEqual(params["filter"], "circle:-71.063,42.357,5000")
        self.assertEqual(params["categories"], "accommodation.hotel")
        self.assertEqual(params["limit"], 100)
        self.assertEqual(data["hotels"][0]["place_id"], "fixed-hotel-1")
        self.assertEqual(data["hotels"][0]["latitude"], 42.358)
        self.assertNotIn("test-secret", json.dumps(data))
        self.assertNotIn("nightly_rate", data["hotels"][0])

    def test_wrong_postcode_country_type_and_invalid_coordinates_stop_before_places(self, _key):
        for changes in [{"postcode":"02109"},{"country_code":"gb"},{"result_type":"city"},{"lat":100},{"lon":181},{"lat":True},{"lat":float('inf')}]:
            with self.subTest(changes=changes), patch("backend.geoapify.httpx.get") as get:
                # Mock json directly to include non-finite values a robust consumer must reject.
                get.return_value.status_code = 200
                get.return_value.json.return_value = {"results": [{**CENTER, **changes}]}
                with self.assertRaises(ZipNotFoundError): search_hotels("02108")
                self.assertEqual(get.call_count, 1)

    def test_missing_fields_stay_null_and_geometry_fallback_is_used(self, _key):
        feature = copy.deepcopy(FEATURE)
        feature["properties"] = {"place_id": "missing-fields"}
        with self.mock_search([feature]): data = search_hotels("02108")
        self.assertIsNone(data["hotels"][0]["name"])
        self.assertIsNone(data["hotels"][0]["address"])
        self.assertEqual(data["hotels"][0]["longitude"], -71.064)

    def test_duplicate_provider_ids_do_not_duplicate_map_results(self, _key):
        with self.mock_search([FEATURE, FEATURE]): data = search_hotels("02108")
        self.assertEqual(data["count"], 1)

    def test_empty_success_is_empty_and_has_center(self, _key):
        with self.mock_search([]): data = search_hotels("02108")
        self.assertEqual(data["count"], 0)
        self.assertEqual(data["center"]["postcode"], "02108")

    def test_all_bad_records_are_failure_not_empty_success(self, _key):
        with self.mock_search([{"properties": {}}]):
            with self.assertRaises(GeoapifyRequestError): search_hotels("02108")

    def test_partial_bad_records_and_outside_radius_are_disclosed(self, _key):
        far = copy.deepcopy(FEATURE)
        far["properties"].update(place_id="far", lat=43.0)
        with self.mock_search([FEATURE, {}, far]): data = search_hotels("02108")
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["omitted_records"], 2)

    def test_request_limit_is_disclosed(self, _key):
        features = []
        for index in range(100):
            feature = copy.deepcopy(FEATURE)
            feature["properties"]["place_id"] = f"fixture-{index}"
            features.append(feature)
        with self.mock_search(features): data = search_hotels("02108")
        self.assertTrue(data["limit_reached"])
        self.assertEqual(data["result_limit"], 100)

    def test_quota_and_service_errors_return_safe_http_responses(self, _key):
        for status, expected in [(429,429),(401,503),(403,503),(500,502)]:
            for stage in ['geocoding','places']:
                calls = [] if stage == 'geocoding' else [response(GEOCODING_URL,{"results":[CENTER]})]
                calls.append(response(PLACES_URL,{"detail":"test-secret-must-not-leak"},status))
                with self.subTest(status=status,stage=stage), patch("backend.geoapify.httpx.get",side_effect=calls):
                    result = TestClient(app).get('/api/hotels?zip_code=02108')
                    self.assertEqual(result.status_code,expected)
                    self.assertNotIn('test-secret',result.text)
                    self.assertNotIn('hotels',result.json())

    def test_network_timeout_is_502(self, _key):
        with patch("backend.geoapify.httpx.get",side_effect=httpx.TimeoutException('URL contains secret')):
            result=TestClient(app).get('/api/hotels?zip_code=02108')
        self.assertEqual(result.status_code,502)
        self.assertNotIn('secret',result.text)

    def test_unresolved_is_404(self, _key):
        with patch("backend.geoapify.httpx.get",return_value=response(GEOCODING_URL,{"results":[]})):
            self.assertEqual(TestClient(app).get('/api/hotels?zip_code=00000').status_code,404)

    def test_invalid_inputs_never_call_provider(self, _key):
        with patch("backend.geoapify.httpx.get") as get:
            for value in ['1234','123456','abcde','１２３４５','02108-1234']:
                self.assertEqual(TestClient(app).get('/api/hotels',params={'zip_code':value}).status_code,422)
            get.assert_not_called()

    def test_malformed_places_payload_is_failure(self, _key):
        with patch("backend.geoapify.httpx.get",side_effect=[response(GEOCODING_URL,{'results':[CENTER]}),response(PLACES_URL,{'features':None})]):
            self.assertEqual(TestClient(app).get('/api/hotels?zip_code=02108').status_code,502)


class LegacyRegressionTests(unittest.TestCase):
    def test_original_search_booking_cancel_delete_and_database_restart(self):
        with tempfile.TemporaryDirectory() as tmp, patch('backend.main.DATABASE_PATH',Path(tmp)/'regression.db'):
            with TestClient(app) as client:
                stays = client.get('/api/stays?query=Harbor').json()['stays']
                self.assertEqual(len(stays),2)
                user = client.get('/api/users').json()[0]['user_id']
                created = client.post('/api/bookings',json={'user_id':user,'trip_id':stays[0]['trip_id']})
                self.assertEqual(created.status_code,201)
                booking_id=created.json()['booking_id']
                self.assertEqual(client.patch(f'/api/bookings/{booking_id}',json={'status':'cancelled'}).status_code,200)
            # A new lifespan reopens/reinitializes the database without overwriting persisted state.
            with TestClient(app) as client:
                history = client.get('/api/bookings',params={'user_id':user}).json()
                self.assertEqual(next(b for b in history if b['booking_id']==booking_id)['status'],'cancelled')
                self.assertEqual(client.delete(f'/api/bookings/{booking_id}').status_code,200)
                self.assertFalse(any(b['booking_id']==booking_id for b in client.get('/api/bookings',params={'user_id':user}).json()))


if __name__ == '__main__': unittest.main()
