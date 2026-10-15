# In-class Activity 2 manual verification

This checklist is for the required student-performed evidence after the automated checks. It intentionally does not claim that these database-browser actions were completed by automation.

## Database Browser setup

1. Start the FastAPI service once so it creates the migration in `data/stayscout.db`.
2. Open `data/stayscout.db` in DB Browser for SQLite and refresh the schema.
3. Confirm the pre-existing `hotels`, `trips`, `users`, and `bookings` tables remain. Confirm the new tables are `saved_hotels`, `saved_hotel_searches`, and `demo_hotel_nights`.
4. Inspect the new tables: `saved_hotels.hotel_id` is the provider identifier; name and address can be null; coordinates are required and range-checked. `demo_hotel_nights` has the composite key `(hotel_id, stay_date)`, nonnegative default rate `10000`, and default rooms `20`.

## Required front-end evidence

1. With the app running, search a live ZIP, select a hotel result, and choose **Add to Local**.
2. In DB Browser, use **Browse Data** to confirm one saved hotel, the ZIP/location association, and five `demo_hotel_nights` rows dated 2026-10-10 through 2026-10-14. The initial values must be 10000 cents and 20 rooms.
3. Refresh the same ZIP in the app. The results header must say **Saved locally**; the saved hotel must show the five local dates, rates, and room counts. Open browser Network tools and confirm the local request is used without a subsequent `/api/hotels` request.
4. Change one row in `demo_hotel_nights` in DB Browser (for example, 2026-10-12 to 12500 cents and 8 rooms), choose **Write Changes**, then repeat the same ZIP search. The edited values should appear.
5. Choose **Remove from Local**, then inspect DB Browser to confirm that hotel’s saved-hotel, ZIP association, and five night rows are deleted. Existing Assignment 1 records and other saved hotels, if any, should still be present.

Automated verification already covers the same behaviors in a temporary database, including duplicate saves, valid date/range constraints, local-first fallback behavior, and cascading removal. It does not replace these required manual DB Browser observations.
