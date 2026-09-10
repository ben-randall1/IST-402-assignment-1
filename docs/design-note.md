# Part 1 design note

The Vue single-page frontend owns the search form, request state, user-facing message, and plain HTML results table. It requests `GET /api/stays?city=...` from FastAPI.

FastAPI validates the city, reads the two CSV files, and returns search-ready records. The backend data logic indexes hotels by `hotel_id`, joins each trip to its hotel, filters by city without regard to letter case, and omits orphaned trips. No database or external service is used in Part 1.
