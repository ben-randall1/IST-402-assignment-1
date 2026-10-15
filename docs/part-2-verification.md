# Part 2 verification — October 8, 2026

**Status:** Implementation and offline verification complete. Successful live LLM verification is blocked by missing `OPENROUTER_API_KEY` and `OPENROUTER_MODEL`. Screenshots and mock traces do not replace the required live recorded demonstration.

## Expected versus observed

| Check / input | Expected | Observed |
| --- | --- | --- |
| Backend unittest discovery | New flow and legacy regressions pass | 45 tests passed, including all 28 pre-existing tests. [Output](evidence/part-2-backend-tests.txt). |
| Frontend Node tests | State, validation, errors, cancel and stale responses pass | 14 tests passed, including 9 pre-existing tests. [Output](evidence/part-2-frontend-tests.txt). |
| Vue production build | Compile both new and existing views | Passed. [Output](evidence/part-2-production-build.txt). |
| Fixed fixture, ZIP 16802, one room Oct 10–12 under $250 | Pine $200; Elm $240; checkout excluded | Mock flow retrieved exactly those two hotels and totals; second call received the original question and exact records. Browser displayed both recommendations and trace. |
| Missing Night / Sold Out fixture hotels | Neither qualifies for the whole stay | Excluded, even when a permissive model query returns all hotel IDs. |
| Deliberately wrong SQL total of 1 cent | Do not trust generated arithmetic | Backend recomputed $200/$240 from authoritative nights. |
| Two rooms, Oct 10–12 | Only Pine with enough rooms throughout; total $400 | Correct independently verified result. |
| October 20–22 (mock model) | No local nightly matches; second call still made | Empty records; frontend explicitly showed no matching local records and suggested changes. |
| Empty saved inventory (mock model) | Empty retrieval, no invented hotels | `no_matches`; answer request received empty records. |
| Model proposes DELETE, UPDATE, DROP, stacked statements, ATTACH, PRAGMA, legacy-table/schema reads, unsafe functions or recursion | Reject, no writes or private legacy reads | 422; database bytes unchanged; second model call not made after rejected proposal. |
| Large cross join / expensive COUNT | Bound rows and computation | 50 rows plus truncation flag; expensive computation interrupted. |
| Invalid dates, missing hotel ID, fabricated citation | Reject invalid contract | Explicit error response. |
| Mock timeout, network error, 429, missing/invalid model, malformed or truncated output | Failure, never successful empty inventory | Correct error mapping; fixture 429, credential-safe messages tested. |
| Keyboard browser submission | Tab to Ask and Enter submits | Correct mock answer displayed. |
| 390 × 844 mobile layout | No horizontal overflow | Document scroll width = viewport width = 390; answer/cards readable. [Screenshot](evidence/part-2-mobile.png). |
| Live Geoapify ZIP `16802` | Exact ZIP, shared list/map | 21 hotels on October 8 at approximately 3:49 PM Eastern. Count is a dated observation, not a fixed assertion. |
| Select Nittany Lion Inn in list; Enter on Scholar map marker | Shared selected hotel | Corresponding controls reported `aria-pressed=true`. |
| Save Nittany Lion Inn and Scholar Hotel State College, repeat ZIP search | Local subset with explicit simulated nights | 2 saved hotels; each had 5 default nightly rows, $100 and 20 simulated rooms per night. [Snapshot](evidence/part-2-local-16802-2026-10-08.json). |
| Stop/restart backend, reload browser and search 16802 | Saved subset survives | Same 2 local hotels and stored data. No new live lookup required. |
| Duplicate saves, edited nights, exact ZIP subset, cascading removal | Preserve local-storage tutorial behavior | Existing isolated-database tests passed; removal and duplicate-save tests do not mutate the working database. |
| Sample stays → Harbor | Preserve Assignment 1 | 2 stays, each $300 simulated total. Booking creation/cancel/delete/persistence regression also passed in a temporary database. |
| Normal chatbot without LLM configuration | Clear setup failure | Browser showed “Chat is not configured…”; no answer or fake empty success. |
| Successful live LLM call | Two real requests and grounded response | **Not run: key/model missing.** |
| Recorded demo, assessed publication, instructor access | Usable evidence and project links | **Pending.** No submission or remote publication performed. |

## Reproduce the fixed fixture

Run `python3 -m backend.verify_part2` from the project root. [Fixture](fixtures/part-2-hotels.json) is explicitly synthetic. [Workflow output](evidence/part-2-mock-workflow.json) contains the question, proposed SQL, records, mock answer, no-match case, rejected DELETE and database-integrity result. To inspect the same flow in Vue, stop the normal backend and run `python3 -m backend.verify_part2 --serve`; start the frontend normally. Return to the normal backend afterward. Mock responses are labeled in the answer and model identity. [Answer screenshot](evidence/part-2-mock-answer.png), [no-match screenshot](evidence/part-2-mock-no-match.png), [rejection screenshot](evidence/part-2-rejected-query.png).

## Corrections and limits

- A SELECT-only prefix was considered insufficient: the final validator also uses SQLite authorization, a read-only connection and a computation budget. Stay totals and full-night availability are independently verified.
- Provider parsing was tightened to reject malformed `choices` elements as a safe service failure rather than allowing an unhandled exception.
- Full-page browser screenshot stitching duplicated portions of the long page; replaced it with readable viewport captures.
- Model-generated SQL can still misinterpret dates, constraints or ordering. Citations are checked for valid record numbers, but free-form prose is not mathematically proven. Read the evidence, especially for questions outside the verified examples. Results are limited to saved local data and 50 rows; no taxes, fees, live availability, amenities or bookings are inferred.
- Cancel stops frontend waiting. It cannot retract a model request already accepted by the server/provider.
- No new dependencies were installed. Credentials stayed in the ignored root `.env`; the working SQLite database remains ignored. The independent in-class DB Browser manual checklist has not been completed by this session.
