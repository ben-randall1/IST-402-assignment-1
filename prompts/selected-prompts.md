# Selected prompts

## Build prompt

Build a travel-stay search application with Vue and FastAPI. The application needs a city input, Search button, clear no-results state, and a plain table of matching hotel stays. The backend must read `hotels.csv` and `trips.csv` and join records using `hotel_id`.

## Verification prompt

Check the application in a browser using one city that has results and one city that has no results. Record the expected and observed outcomes for the Part 1 report.

## Part 2 build prompt

Extend the travel application with SQLite persistence. Seed the supplied hotel, trip, user, and booking CSV files once; then use SQLite for every read and write. Add frontend controls to create a booking, read booking history, cancel a booking while keeping it in history, and delete a test booking.

## Part 2 verification prompt

Demonstrate search, create, read, cancel, and delete in the browser. Refresh the browser and restart the backend between update and delete checks to confirm the SQLite changes persist without re-seeding or duplicating the starter records.
