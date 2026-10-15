> **Assignment 3.1 — Research and Design:** see [A little space](assignment-3/README.md) and the current [submission report](report.md). The StayScout application and startup instructions below remain the Assignment 2 project. Its prior report is [archived here](docs/assignment-2-part-2-report.md).

# StayScout · Assignment 2.2

Live hotel discovery with Vue 3, FastAPI, Geoapify, and Leaflet. Enter a five-digit U.S. ZIP; explore the same nearby hotels in a numbered list and map. Existing SQLite sample stays and simulated booking CRUD are preserved under **Sample stays**.

**Ask StayScout** adds a two-request RAG assistant over saved local hotels and simulated nightly data. The backend asks a free OpenRouter Nemotron model to propose SQL, validates and executes it read-only, then asks the model to explain the retrieved records. SQL, records, model identity and answer are visible in the evidence disclosure. Live LLM verification requires your configured key and currently available class model; fixture demonstrations are explicitly labeled mocks.

## Run locally

Requirements: Node 22.12+ (tested 22.19), Python 3.11+, and a free Geoapify API key.

For a fresh checkout, check installed dependencies first. The assignment's CHECK → TAKE ACTION → VERIFY rule requires student approval before installing missing packages. This session added only the approved `leaflet@1.9.4`; existing Vue/Vite and Python packages were reused.

```sh
# On a fresh checkout, after approving missing dependencies:
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
npm --prefix frontend ci
```

Copy `.env.example` to `.env` only if you do not already have `.env`; set `GEOAPIFY_API_KEY` in that local file. Never add `VITE_GEOAPIFY_API_KEY`, and never commit `.env`. This working copy already has local configuration, so do not overwrite it. The original project's `.venv` lacks httpx; the current machine's system `python3` has all required backend packages.

For the chatbot, add `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` to the same ignored root `.env` using a local editor. The model must be a currently available `nvidia/...nemotron...:free` ID from the class configuration. Check [current models](https://openrouter.ai/models?fmt=free) and [usage limits](https://openrouter.ai/docs/api_reference/limits); availability is not guaranteed. No paid fallback is enabled. Never put either key in a frontend `VITE_` variable or paste it into reports. Configuration is reread per request. No new dependency is needed for Part 2.

Start in the project root, using two terminals:

```sh
# Terminal 1: on this machine (or substitute .venv/bin/python after a fresh setup)
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

# Terminal 2
npm --prefix frontend run dev
```

Open **http://127.0.0.1:5173/**. Vite forwards `/api` to `127.0.0.1:8000`. Both services bind locally. Stop with Ctrl+C. Internet access is required for live provider requests, map tiles, and optional Google Fonts (system fonts provide a fallback).

## Verify

```sh
python3 -m unittest discover -s backend -t . -v
npm --prefix frontend test
npm --prefix frontend run build
python3 -m backend.verify_part2
git check-ignore .env
git ls-files .env
```

The backend suite mocks upstream calls; frontend tests use Node's built-in test runner with stubbed fetch. Neither automated suite spends API credits. The SQLite regression uses a temporary database and never mutates the working database. The last command should print nothing.

## Architecture and contract

- `backend/main.py`: HTTP routes, existing SQLite sample data and simulated bookings.
- `backend/geoapify.py`: geocoding, exact country/postcode validation, bounded Places request, data normalization, safe failures.
- `backend/models.py`: external hotel structure, independent of the sample `hotels` table and its required nightly rate.
- `frontend/src/composables/useHotelSearch.js`: request state, stale-request protection, and shared selection.
- `frontend/src/components/HotelMap.vue`: Leaflet map, numbered keyboard-selectable markers, radius and attribution.
- `frontend/src/components/LegacyStays.vue`: preserved Assignment 1 UI with its original styles scoped to the component.

`GET /api/hotels?zip_code=16802` returns a verified `center`, normalized `hotels`, `count`, `radius_meters`, `result_limit`, `limit_reached`, `omitted_records`, `observed_at`, and `source`. A hotel contains `provider`, `place_id`, nullable `name` and `address`, `latitude`, `longitude`, and calculated `distance_meters`. No price, rating, or availability field is inferred from the provider.

HTTP outcomes: 422 invalid input, 404 no verified ZIP, 429 provider quota/rate limit, 502 upstream transport/payload failure, and 503 missing/unauthorized backend credential. Successful empty results return 200 with a verified center and an empty hotel array.

The search uses `accommodation.hotel`, a 5,000-meter circle around the returned ZIP point, proximity ordering and a 100-record cap. Returned coordinates must be finite and valid. Duplicate provider IDs are collapsed; invalid and out-of-radius records are omitted and counted. A nonempty but wholly unusable response is a failure rather than a misleading empty success. The search is not an exhaustive hotel inventory, not the complete ZIP boundary, and not evidence of rooms available to book. Distances are straight-line estimates.

Geoapify requests stay in FastAPI. The browser uses public HTTPS OpenStreetMap tiles, with visible attribution and normal browser caching. Searches occur only on explicit submission or a destination shortcut, not keystrokes or map movements.

See [research](docs/research.md), [early mockup](docs/early-mockup.svg), [report](report.md), [verification](docs/verification.md), and [demo recording outline](docs/demo-script.md).

## In-class Activity 2: local hotel storage

The Explore view first calls `GET /api/local-hotels?zip_code=...`. A nonempty local result displays only that saved subset and its stored simulated classroom values; a successful empty local result falls back to the existing Part 1 `GET /api/hotels` search. A local-storage error remains an error and never silently falls back to the provider.

`POST /api/local-hotels` saves the provider ID, nullable name/address, coordinates, exact searched ZIP/location, and five default nights for 2026-10-10 through 2026-10-14. Repeating a save is non-destructive. `DELETE /api/local-hotels/{hotel_id}` removes the hotel, its ZIP associations, and its night rows in one transaction. The original Assignment 1 hotel/trip/booking records remain separate.

See the [manual DB Browser checklist](docs/activity-2-manual-verification.md) for the required student-performed activity evidence.

## Part 2: ask about saved hotels

1. In **Explore hotels**, search `16802` and save two hotels with **Add to Local**. Repeat the search to see the saved local subset. The default simulated dates are October 10–14, 2026, at $100/night with 20 rooms; existing stored edits survive repeated saves.
2. Open **Ask StayScout**. Ask: “Which saved hotels in ZIP 16802 have a room from October 10 to October 12, 2026, for under $250 total? Compare the total costs.” Expected with unchanged default nights: $200 for each complete two-night stay; October 12 is checkout and excluded.
3. Open **How this answer was found**. Compare the proposed SQL, exact retrieved records, independently recalculated totals, and answer. Questions are independent, not conversational memory.
4. Ask about October 20–22, 2026. Without those nights, expect no matching local records. Provider failures are errors, never empty successes.

`POST /api/chat` takes `{"question":"..."}` (1–1,200 characters). It returns `question`, `proposed_sql`, normalized `sql`, `records`, `stay`, `answer`, `citations`, `status`, `truncated`, `excluded_incomplete_stays`, `model`, `model_requests`, `simulated`, and `observed_at`. HTTP outcomes: 422 invalid input/query, 429 model limit, 502 malformed/failed model response, 503 configuration/storage unavailable, 504 model timeout. No raw provider error body is exposed.

SQL is restricted by SQLite's authorizer to the three local tables and allowlisted functions. The database connection uses `mode=ro` and query-only mode. One SELECT/WITH, no recursion, no comments/multiple statements, at most 50 returned rows, 60 KB retrieved JSON, and bounded execution. Stay candidates are rechecked against all nightly rows in the same snapshot before the second request. This prevents writes and missing-night availability claims; it cannot prove the LLM fully understood arbitrary user intent. Check the trace before relying on a recommendation.

### Reproduce offline evidence

`python3 -m backend.verify_part2` creates a temporary database from [the synthetic fixed JSON fixture](docs/fixtures/part-2-hotels.json), mocks both model outputs, and writes [the workflow evidence](docs/evidence/part-2-mock-workflow.json). It verifies a $200/$240 comparison, no matches, a rejected DELETE, an unchanged database and a mocked 429. No credits or working records are used.

For the same browser checks, stop the normal backend, run `python3 -m backend.verify_part2 --serve`, and use the regular frontend. The fixture model recognizes the supplied comparison, October 20–22, “Delete all saved hotels”, and “Trigger the mocked rate limit”. It is deterministic, not a working natural-language model. Stop it before restarting the normal backend; the normal app has no fixture switch.

See [Part 2 research](docs/part-2-research.md), [early mockup](docs/part-2-early-mockup.svg), [verification](docs/part-2-verification.md), [recording outline](docs/part-2-demo-script.md), and the [archived Part 1 report](docs/part-1-report.md).
