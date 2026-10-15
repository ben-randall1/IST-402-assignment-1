"""Offline evidence runner: python3 -m backend.verify_part2 [--serve].

Uses a temporary database and mocked model; never changes the working database
or calls OpenRouter. --serve runs the actual FastAPI routes for browser checks.
"""
import argparse
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import uvicorn
from fastapi.testclient import TestClient

from . import chat, main
from .test_chat import FIXTURE, seed_fixture


class EvidenceModel:
    model = "MOCK — deterministic fixture, not a live model"

    def complete(self, system, payload):
        if system == chat.QUERY_RULES:
            question = payload["question"].lower()
            if "delete" in question:
                return {"sql": "DELETE FROM saved_hotels", "stay": None}
            if "rate limit" in question:
                raise chat.ChatError("MOCK: free model usage limit reached.", 429)
            if "20" in question and "22" in question:
                return {"sql": FIXTURE["sql"].replace("2026-10-10", "2026-10-20").replace("2026-10-12", "2026-10-22"), "stay": {"check_in": "2026-10-20", "check_out": "2026-10-22", "rooms": 1}}
            return {"sql": FIXTURE["sql"], "stay": FIXTURE["stay"]}
        if payload["records"]:
            return {"answer": "MOCK MODEL RESPONSE — " + FIXTURE["mock_answer"], "citations": [1, 2]}
        return {"answer": "MOCK MODEL RESPONSE — No matching local records for October 20–22, 2026. The saved simulated nights do not cover this stay. Try October 10–12 or save hotels with the requested nights. This does not establish real hotel availability.", "citations": []}


def main_cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="stayscout-part2-") as directory:
        database = Path(directory) / "fixture.db"
        with patch("backend.main.DATABASE_PATH", database), patch("backend.chat.OpenRouterModel", EvidenceModel):
            main.initialize_database()
            seed_fixture(database)
            if args.serve:
                print("OFFLINE FIXTURE SERVER: synthetic hotels and mocked model, temporary database; no live AI calls.", flush=True)
                uvicorn.run(main.app, host="127.0.0.1", port=8000)
                return
            before = database.read_bytes()
            with TestClient(main.app) as client:
                success = client.post("/api/chat", json={"question": FIXTURE["question"]})
                no_match = client.post("/api/chat", json={"question": "Which hotels have rooms October 20–22, 2026?"})
                rejected = client.post("/api/chat", json={"question": "Delete all saved hotels"})
                rate_limited = client.post("/api/chat", json={"question": "Trigger the mocked rate limit"})
            assert success.status_code == 200 and no_match.status_code == 200
            assert [r["total_cost_cents"] for r in success.json()["records"]] == [20000, 24000]
            assert no_match.json()["records"] == [] and no_match.json()["status"] == "no_matches"
            assert rejected.status_code == 422 and rate_limited.status_code == 429
            unchanged = before == database.read_bytes()
            assert unchanged
            evidence = {"label": "OFFLINE MOCK EVIDENCE — not live LLM calls", "observed_at": datetime.now(timezone.utc).isoformat(), "fixture": "docs/fixtures/part-2-hotels.json", "successful_question": success.json(), "no_match": no_match.json(), "rejected_query": {"proposed_sql": "DELETE FROM saved_hotels", "status": rejected.status_code, "response": rejected.json(), "database_bytes_unchanged": unchanged}, "rate_limit": {"status": rate_limited.status_code, "response": rate_limited.json()}}
            output = main.PROJECT_ROOT / "docs/evidence/part-2-mock-workflow.json"
            output.write_text(json.dumps(evidence, indent=2) + "\n")
            print(f"PASS: success, no match, rejection, rate limit; unchanged database. Evidence: {output}")


if __name__ == "__main__":
    main_cli()
