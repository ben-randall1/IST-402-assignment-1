# Part 2 design note

The Vue single-page frontend owns the hotel-name search form, demo traveler selection, booking controls, messages, and plain HTML tables for stays and booking history. It sends all search and CRUD requests to FastAPI.

FastAPI initializes a local SQLite database once from the four supplied CSV files. After seeding, the backend handles all searches and booking create, read, update, and delete actions through SQLite. It joins hotels, trips, users, and bookings for display, derives nights and stay price, and preserves new records and changes across restarts.
