"""Repeatable Part 2 tests. All model responses are mocks; no API credits used."""
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import httpx
from fastapi.testclient import TestClient

from backend import chat, main

FIXTURE_PATH = main.PROJECT_ROOT / "docs/fixtures/part-2-hotels.json"
FIXTURE = json.loads(FIXTURE_PATH.read_text())


def seed_fixture(database):
    with sqlite3.connect(database) as connection:
        for hotel in FIXTURE["hotels"]:
            connection.execute("INSERT INTO saved_hotels VALUES (?, ?, ?, ?, ?)",
                               tuple(hotel[k] for k in ["hotel_id", "name", "address", "latitude", "longitude"]))
            connection.execute("INSERT INTO saved_hotel_searches VALUES (?, '16802', 'us', 40.803, -77.861, 'State College (fixture)')", (hotel["hotel_id"],))
            connection.executemany("INSERT INTO demo_hotel_nights VALUES (?, ?, ?, ?)", [(hotel["hotel_id"], *night) for night in hotel["nights"]])


def fixture_model(sql=None, stay=None, answer=None):
    model = Mock()
    model.model = "MOCK — deterministic fixture, not a live model"
    model.complete.side_effect = [
        {"sql": sql or FIXTURE["sql"], "stay": stay or FIXTURE["stay"]},
        answer or {"answer": FIXTURE["mock_answer"], "citations": [1, 2]},
    ]
    return model


class ChatTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database = Path(self.temp.name) / "test.db"
        self.db_patch = patch("backend.main.DATABASE_PATH", self.database)
        self.db_patch.start()
        self.context = TestClient(main.app)
        self.client = self.context.__enter__()
        seed_fixture(self.database)

    def tearDown(self):
        self.context.__exit__(None, None, None)
        self.db_patch.stop()
        self.temp.cleanup()

    def test_complete_two_request_flow_and_grounding_context(self):
        model = fixture_model()
        with patch("backend.chat.OpenRouterModel", return_value=model):
            response = self.client.post("/api/chat", json={"question": FIXTURE["question"]})
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["model_requests"], 2)
        self.assertEqual([r["hotel_id"] for r in result["records"]], FIXTURE["expected"]["hotel_ids"])
        self.assertEqual([r["total_cost_cents"] for r in result["records"]], [20000, 24000])
        self.assertEqual(result["answer"], FIXTURE["mock_answer"])
        first, second = model.complete.call_args_list
        self.assertIn("saved_hotels", first.args[0])
        self.assertEqual(first.args[1]["question"], FIXTURE["question"])
        self.assertEqual(second.args[1]["question"], FIXTURE["question"])
        self.assertEqual(second.args[1]["records"], result["records"])

    def test_missing_soldout_nights_and_wrong_generated_total_are_checked(self):
        result = chat.retrieve(self.database, "SELECT hotel_id, 1 AS total_cost_cents FROM saved_hotels ORDER BY hotel_id", chat.validate_stay(FIXTURE["stay"]))
        self.assertEqual(result["excluded_incomplete_stays"], 2)
        self.assertEqual({r["hotel_id"]: r["total_cost_cents"] for r in result["records"]}, {"fixture-pine": 20000, "fixture-elm": 24000})
        self.assertEqual(len(result["records"][0]["nightly_records"]), 2)

    def test_multi_room_stay_multiplies_total_and_checks_every_night(self):
        stay = chat.validate_stay({**FIXTURE["stay"], "rooms": 2})
        result = chat.retrieve(self.database, "SELECT hotel_id FROM saved_hotels", stay)
        self.assertEqual(len(result["records"]), 1)
        self.assertEqual(result["records"][0]["total_cost_cents"], 40000)

    def test_no_match_still_calls_answer_model_with_empty_records(self):
        model = fixture_model(sql=FIXTURE["sql"].replace("2026-10-10", "2026-10-20").replace("2026-10-12", "2026-10-22"), stay={"check_in": "2026-10-20", "check_out": "2026-10-22", "rooms": 1}, answer={"answer": "No matching local records. Try the stored October 10–14 demo dates or save more hotels. These are simulated values.", "citations": []})
        result = chat.answer_question(self.database, "Any hotels October 20–22, 2026?", model)
        self.assertEqual(result["status"], "no_matches")
        self.assertEqual(model.complete.call_count, 2)
        self.assertEqual(model.complete.call_args.args[1]["records"], [])

    def test_empty_inventory_is_not_provider_failure(self):
        with sqlite3.connect(self.database) as connection:
            connection.execute("DELETE FROM saved_hotels")
        model = fixture_model(answer={"answer": "No matching saved hotels. Add hotels in Explore first. Prices are simulated.", "citations": []})
        self.assertEqual(chat.answer_question(self.database, FIXTURE["question"], model)["status"], "no_matches")

    def test_disallowed_queries_cannot_change_or_read_legacy_data(self):
        before = self.database.read_bytes()
        queries = [
            "DELETE FROM saved_hotels", "UPDATE demo_hotel_nights SET rooms_available=999",
            "DROP TABLE saved_hotels", "SELECT * FROM saved_hotels; DELETE FROM saved_hotels",
            "PRAGMA user_version=9", "ATTACH DATABASE '/tmp/x' AS x",
            "SELECT * FROM users", "SELECT * FROM bookings", "SELECT * FROM sqlite_master",
            "SELECT load_extension('bad') FROM saved_hotels", "SELECT randomblob(1000000000) FROM saved_hotels",
            "WITH x AS (SELECT * FROM users) SELECT * FROM x",
            "WITH RECURSIVE x(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM x) SELECT * FROM x",
            "SELECT 'invented hotel' AS name", "SELECT * FROM pragma_table_info('users')",
        ]
        for sql in queries:
            with self.subTest(sql=sql), self.assertRaises(chat.ChatError) as error:
                chat.retrieve(self.database, sql)
            self.assertEqual(error.exception.status, 422)
        self.assertEqual(self.database.read_bytes(), before)

    def test_invalid_sql_prevents_second_model_request(self):
        model = fixture_model(sql="DELETE FROM saved_hotels")
        with patch("backend.chat.OpenRouterModel", return_value=model):
            response = self.client.post("/api/chat", json={"question": "Delete every hotel"})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(model.complete.call_count, 1)

    def test_nonrecursive_cte_and_leading_zero_zip(self):
        with sqlite3.connect(self.database) as connection:
            connection.execute("UPDATE saved_hotel_searches SET zip_code='02108'")
        result = chat.retrieve(self.database, "WITH places AS (SELECT hotel_id FROM saved_hotel_searches WHERE zip_code='02108') SELECT * FROM places")
        self.assertEqual(len(result["records"]), 4)

    def test_rows_and_computation_are_bounded(self):
        result = chat.retrieve(self.database, "SELECT a.hotel_id AS a,b.hotel_id AS b,c.hotel_id AS c FROM saved_hotels a CROSS JOIN saved_hotels b CROSS JOIN saved_hotels c")
        self.assertEqual(len(result["records"]), 50)
        self.assertTrue(result["truncated"])
        sql = "SELECT COUNT(*) FROM " + " CROSS JOIN ".join(f"saved_hotels t{i}" for i in range(14))
        with self.assertRaises(chat.ChatError):
            chat.retrieve(self.database, sql)

    def test_invalid_dates_missing_id_and_citations_rejected(self):
        for stay in [{**FIXTURE["stay"], "rooms": True}, {**FIXTURE["stay"], "check_out": "2026-10-09"}, {**FIXTURE["stay"], "check_in": "2026-02-30"}]:
            with self.assertRaises(chat.ChatError):
                chat.validate_stay(stay)
        with self.assertRaises(chat.ChatError):
            chat.retrieve(self.database, "SELECT name FROM saved_hotels", chat.validate_stay(FIXTURE["stay"]))
        for citations in [[], [999], [True]]:
            with self.subTest(citations=citations), self.assertRaises(chat.ChatError):
                chat.answer_question(self.database, FIXTURE["question"], fixture_model(answer={"answer": "Unsupported", "citations": citations}))

    def test_input_validation_and_missing_configuration(self):
        for value in ["", "  ", "a" * 1201]:
            self.assertEqual(self.client.post("/api/chat", json={"question": value}).status_code, 422)
        with patch("backend.chat.dotenv_values", return_value={}), patch.dict("os.environ", {}, clear=True):
            response = self.client.post("/api/chat", json={"question": "Which hotels are saved?"})
        self.assertEqual(response.status_code, 503)
        self.assertIn("not configured", response.json()["detail"])

    def test_error_mapping_and_no_successful_empty_on_failure(self):
        for status in [429, 502, 503, 504]:
            with patch("backend.main.answer_question", side_effect=chat.ChatError("Safe message", status)):
                response = self.client.post("/api/chat", json={"question": "Which hotels?"})
            self.assertEqual(response.status_code, status)
            self.assertNotIn("records", response.json())
            if status == 429:
                self.assertEqual(response.headers["Retry-After"], "60")


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.config = patch("backend.chat.settings", return_value=("secret-test-key", "nvidia/fixture-nemotron:free"))
        self.config.start()
        self.model = chat.OpenRouterModel()

    def tearDown(self):
        self.config.stop()

    def call_response(self, response):
        with patch("backend.chat.httpx.Client") as client:
            client.return_value.__enter__.return_value.post.return_value = response
            result = self.model.complete("rules", {"question": "which?"})
            request = client.return_value.__enter__.return_value.post.call_args
            self.assertEqual(request.kwargs["headers"]["Authorization"], "Bearer secret-test-key")
            self.assertNotIn("secret-test-key", json.dumps(request.kwargs["json"]))
            return result

    def test_correct_request_and_json_response(self):
        result = self.call_response(httpx.Response(200, json={"choices": [{"finish_reason": "stop", "message": {"content": '{"sql":"SELECT * FROM saved_hotels", "stay":null}'}}]}))
        self.assertIn("sql", result)

    def test_provider_failures_are_credential_safe(self):
        for status, expected in [(429, 429), (401, 503), (402, 503), (404, 503), (500, 502)]:
            with self.subTest(status=status), self.assertRaises(chat.ChatError) as error:
                self.call_response(httpx.Response(status, text="secret-test-key provider details"))
            self.assertEqual(error.exception.status, expected)
            self.assertNotIn("secret-test-key", str(error.exception))

    def test_malformed_truncated_and_reflected_secret_are_rejected(self):
        for body in [{}, {"choices": []}, {"choices": ["invalid"]}, {"choices": [{"finish_reason": "length", "message": {"content": '{}'}}]}, {"choices": [{"finish_reason": "stop", "message": {"content": 'not json'}}]}, {"choices": [{"finish_reason": "stop", "message": {"content": '{"answer":"secret-test-key"}'}}]}]:
            with self.subTest(body=body), self.assertRaises(chat.ChatError):
                self.call_response(httpx.Response(200, json=body))

    def test_timeout_network_failures(self):
        for failure in [httpx.ConnectError("secret-test-key"), httpx.ReadTimeout("secret-test-key")]:
            with patch("backend.chat.httpx.Client") as client:
                client.return_value.__enter__.return_value.post.side_effect = failure
                with self.assertRaises(chat.ChatError) as error:
                    self.model.complete("rules", {})
            self.assertNotIn("secret-test-key", str(error.exception))

    def test_paid_or_non_nemotron_model_rejected(self):
        self.config.stop()
        for model in ["openai/paid", "nvidia/nemotron:paid", "openrouter/free"]:
            with patch.dict("os.environ", {"OPENROUTER_API_KEY": "secret-test-key", "OPENROUTER_MODEL": model}), self.assertRaises(chat.ChatError):
                chat.settings()


if __name__ == "__main__":
    unittest.main()
