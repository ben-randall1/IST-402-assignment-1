# StayScout · Assignment 2.1

Live hotel discovery with Vue 3, FastAPI, Geoapify, and Leaflet. Enter a five-digit U.S. ZIP; explore the same nearby hotels in a numbered list and map. Existing SQLite sample stays and simulated booking CRUD are preserved under **Sample stays**.

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

`GET /api/hotels?zip_code=16802` returns a verified `center`, normalized `hotels`, `count`, `radius_meters`, `result_limit`, `limit_reached`, `omitted_records`, `observed_at`, and `source`. A hotel contains `provider`, `place_id`, nullable `name` and `address`, `latitude`, `longitude`, and calculated `distance_meters`. No price, rating, or availability field is inferred. Part 2 can persist these snapshots separately without changing the sample Hotel model.

HTTP outcomes: 422 invalid input, 404 no verified ZIP, 429 provider quota/rate limit, 502 upstream transport/payload failure, and 503 missing/unauthorized backend credential. Successful empty results return 200 with a verified center and an empty hotel array.

The search uses `accommodation.hotel`, a 5,000-meter circle around the returned ZIP point, proximity ordering and a 100-record cap. Returned coordinates must be finite and valid. Duplicate provider IDs are collapsed; invalid and out-of-radius records are omitted and counted. A nonempty but wholly unusable response is a failure rather than a misleading empty success. The search is not an exhaustive hotel inventory, not the complete ZIP boundary, and not evidence of rooms available to book. Distances are straight-line estimates.

Geoapify requests stay in FastAPI. The browser uses public HTTPS OpenStreetMap tiles, with visible attribution and normal browser caching. Searches occur only on explicit submission or a destination shortcut, not keystrokes or map movements.

See [research](docs/research.md), [early mockup](docs/early-mockup.svg), [report](report.md), [verification](docs/verification.md), and [demo recording outline](docs/demo-script.md).

## Part 2 boundary

The persistent live-hotel shortlist is not implemented in Part 1. Existing SQLite booking persistence belongs to the original sample application and must not be presented as Part 2 shortlist completion.
