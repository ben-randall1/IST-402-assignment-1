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

Remaining limitation: the repository is private and screenshots still need instructor-accessible links before submission. Next task: merge and push the reviewed Part 2 work, then upload this updated `report.md` to the Part 2 submission page.
