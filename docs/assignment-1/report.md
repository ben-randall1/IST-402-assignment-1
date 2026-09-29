# StayScout — In-class Public API Integration

## Implementation and current verification

The existing Vue and FastAPI travel application now has a backend-only Geoapify ZIP lookup. A key-free project-root `.env` setting is ignored by Git, and `backend/config.py` explicitly loads it. `/api/health` exposes only the configuration status—not the value. `backend/geoapify.py` calls Geoapify forward geocoding with a five-digit postcode, `type=postcode`, U.S. country filtering, JSON format, and a 10-second timeout. It accepts only a result that matches the requested U.S. postcode and has usable coordinates, returning a small payload: postcode, country code, latitude, longitude, and locality when available.

`/api/demo/zip-location` supplies the required fixed 16802 demonstration. `/api/zip-location?zip_code=16802` accepts a real five-digit ZIP code, including leading zeroes. Vue adds the fixed **Look up ZIP 16802** button, an entered-ZIP form, loading and safe error feedback, and a plain returned-location table. The existing hotel search still works.

## Verification evidence — September 24, 2026

| Check | Observed result |
| --- | --- |
| Mocked controller and route checks | `python3 -m unittest backend.test_geoapify backend.test_zip_routes -v` passed 6 tests: verified success, mismatched postcode rejection, sanitized provider failure, fixed route, safe missing-key route, and a leading-zero entered ZIP. |
| Backend and frontend build | `python3 -m compileall -q backend` and `npm --prefix frontend run build` passed. |
| Health URL | Local `http://127.0.0.1:8000/api/health` returned HTTP 200 and reported `key is not configured`, without a key value. |
| Fixed demo URL | Local `/api/demo/zip-location` returned the expected credential-safe HTTP 503 configuration message because no local key is present. |
| Browser interface | The fixed button showed the safe configuration error; a four-digit entry showed five-digit validation; existing `Harbor` hotel search still returned 2 stays. |

### Live-data verification and next evidence

After the local Geoapify key was refreshed and FastAPI restarted, `/api/health` returned HTTP 200 with `key is configured`. The fixed `/api/demo/zip-location` request returned HTTP 200 for ZIP 16802 with `State College`, `US`, latitude `40.803167822`, and longitude `-77.861384958`. The visible Vue interface returned the same values in its ZIP location table after the **Look up ZIP 16802** button was clicked.

Capture a screenshot showing the entered ZIP and returned table. Do not show `.env` or an API key, then submit that evidence and state the health-check configuration status in Canvas.

# StayScout — Part 2

## Repository and commit

GitHub repository: [ben-randall1/IST-402-assignment-1](https://github.com/ben-randall1/IST-402-assignment-1). Part 1 implementation checkpoint: `8ac03e41e47ddf32e560bcaf664229a7944a656b`. Exact Part 2 merged implementation commit: `d510b702b896a20e8ac92bd41c7dee26cac75743` (`merge: add Part 2 SQLite CRUD`).

## Implementation

Part 2 replaces the Part 1 CSV-only runtime with a local SQLite database. On its first start, FastAPI creates the schema and seeds hotels, trips, users, and bookings from the supplied CSVs. Later starts do not import those files again. FastAPI uses SQLite for hotel-name searches and all booking create, read, update, and delete operations. Vue provides the hotel search, traveler picker, Book this stay buttons, booking-history table, Cancel action, and Delete action.

## Verification

I manually reviewed the Vue, FastAPI, SQLite schema, and project documentation in VS Code/source files. `sqlite3` was available in the project Python interpreter (SQLite 3.42.0), passed a create/close/reopen persistence check, and `npm run build` completed successfully.

| Action | Expected result | Observed result |
| --- | --- | --- |
| Search `Harbor` | Matching hotel stays appear from SQLite. | Two Harbor Lantern Hotel stays appeared with clear labels and Book this stay controls. |
| Search `Not A Hotel` | A clear no-results message appears. | “No hotel stays match ‘Not A Hotel’. Try another hotel name.” appeared. |
| Create | A new booking is stored and shown in history. | A new `B8AAC612B` booking for Demo Traveler 6 was created as confirmed and immediately appeared in history. |
| Read | The selected traveler’s stored bookings appear. | Demo Traveler 6’s new booking appeared in the history table. |
| Update | Cancelling retains the record with cancelled status. | `B8AAC612B` changed to Cancelled and remained in the table. |
| Persistence | Changes remain after browser refresh and backend restart, without duplicate seed data. | The cancelled booking remained after both checks; no starter records were duplicated. |
| Delete | The test booking is removed. | `B8AAC612B` was deleted through the frontend and Demo Traveler 6’s history returned to empty. |

## Project context and next steps

Project documentation: [README](README.md), [AGENTS.md](AGENTS.md), [design note](docs/design-note.md), [selected prompts](prompts/selected-prompts.md), and [current handoff](handoffs/current.md).

Remaining limitation: the repository is private and screenshots still need instructor-accessible links before submission. Next task: grant the instructor repository access, add screenshot links, and upload this updated `report.md` to the Part 2 submission page.
