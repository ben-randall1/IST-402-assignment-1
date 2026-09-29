# StayScout

A Vue, FastAPI, and SQLite travel-stay application for IST 402 Assignment 1, Part 2.

## Geoapify ZIP lookup configuration

The project-root `.env` file holds the local-only `GEOAPIFY_API_KEY` setting and is ignored by Git. Add a Geoapify key after the equals sign locally; never place it in frontend code, a `VITE_` variable, screenshots, or a submission. The backend loads that exact project-root file through `backend/config.py`. Restart the FastAPI backend after editing `.env` so it reads the current configuration.

`GET /api/health` reports `key is configured` or `key is not configured` without returning the key. `GET /api/demo/zip-location` performs the fixed 16802 in-class check, and `GET /api/zip-location?zip_code=16802` supports the frontend's entered ZIP lookup. Geoapify responses are reduced to the verified postcode, country code, coordinates, and locality when available.

## Requirements

- Python 3.11+
- Node.js 20+

## Run locally

1. Create and activate a Python virtual environment (optional but recommended):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install and run the API from the project root:

   ```bash
   pip install -r backend/requirements.txt
   uvicorn backend.main:app --reload --port 8000
   ```

3. In a second terminal, install and run the Vue app:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. Open the address printed by Vite (normally `http://localhost:5173`). Search for a hotel name such as `Harbor`, select a demo traveler, then create and manage simulated bookings.

   The ZIP lookup panel also provides a fixed **Look up ZIP 16802** demonstration button and a five-digit U.S. ZIP input. Run the backend in a separate terminal first.

## Data

On the first API startup, the backend seeds `data/stayscout.db` from the instructor-provided `hotels.csv`, `trips.csv`, `users.csv`, and `bookings.csv` files. After that, every search and booking action reads from or writes to SQLite; CSVs are not re-imported, so bookings survive browser and API restarts. The SQLite database is intentionally ignored by Git because it is local runtime data.

## Part 2 features

- Search available stays by hotel name.
- Select a demo traveler and create a confirmed simulated booking.
- Read that traveler's booking history.
- Cancel a booking without removing its history record.
- Delete a test booking.

## Project context

- [Design note](docs/design-note.md)
- [Selected prompts](prompts/selected-prompts.md)
- [Current handoff](handoffs/current.md)
