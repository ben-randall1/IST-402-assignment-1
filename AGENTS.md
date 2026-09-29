# Project guidance

- Keep the frontend in `frontend/` and the FastAPI service in `backend/`.
- Preserve the `hotel_id` join between `data/hotels.csv` and `data/trips.csv`.
- Assignment 2.1 replaces the main view with live ZIP search and a synchronized Leaflet map/list. Preserve Assignment 1's sample booking UI in a clearly labeled separate view.
- After a change, run the relevant check and record the result in `handoffs/current.md` and `report.md` when appropriate.

## MVC responsibilities

- Model: existing SQLite sample hotel/trip/booking records remain separate from `backend/models.py` external place records. External places have a provider ID, optional name/address, coordinates and calculated distance; never infer prices, ratings, availability, or booking confirmations.
- Controller: FastAPI routes validate request inputs and map domain failures to HTTP responses. `backend/geoapify.py` owns provider requests, U.S. postcode verification, normalization, and credential-safe errors. Frontend composables own request state and shared selection.
- View: Vue components render state and emit user actions. Leaflet renders the same hotel collection and selected identifier as the list. Escape provider content.

## CHECK → TAKE ACTION → VERIFY

1. CHECK existing code, installed versions, configuration and behavior. Before adding a dependency, explain the exact package and installation command and obtain the student's approval.
2. TAKE ACTION only within that approved installation scope. Keep credentials in ignored root `.env`; never expose backend keys in frontend variables, responses, logs, screenshots or reports.
3. VERIFY with relevant unittest cases, a production Vue build and browser checks. Compare expected and observed results; do not claim a check was run if it was only planned. Record a live ZIP and observation date. Mock empty, malformed, network and 429 responses rather than spending quota to force them.
4. Preserve existing behavior and run legacy regressions when shared code changes. Never treat a failed request as successful empty results. Do not submit or publish unfinished evidence as complete.

## Approved dependency action — 2026-09-29

The student approved `npm install --save-exact leaflet@1.9.4` after the environment check established that Vue/Vite and the required system Python packages were present but Leaflet was missing. No other dependency installation was approved in that exchange.
