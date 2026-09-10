# StayScout

A Vue and FastAPI travel-stay search application for IST 402 Assignment 1, Part 1.

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

4. Open the address printed by Vite (normally `http://localhost:5173`). Search for `Boston`, `Miami`, or `Seattle`.

## Data

The API reads `data/hotels.csv` and `data/trips.csv` on every request and joins each trip to its hotel using `hotel_id`. The included files are small demo data so the project runs immediately. Replace them with the instructor-provided `hotels.csv` and `trips.csv` before submission if different data is required; retain their file names and the `hotel_id` column.

## Project context

- [Design note](docs/design-note.md)
- [Selected prompts](prompts/selected-prompts.md)
- [Current handoff](handoffs/current.md)
