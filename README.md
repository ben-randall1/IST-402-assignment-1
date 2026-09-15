# StayScout

A Vue, FastAPI, and SQLite travel-stay application for IST 402 Assignment 1, Part 2.

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
