# Assignment 2.2 — Business Intelligence with RAG and an LLM

**Student:** Ben Randall
**Course:** IST 402, Section 003
**Project:** StayScout
**Observation date:** October 8, 2026

> **Submission status: not ready to submit.** The implementation, automated checks, fixture-based browser demonstration, and live hotel-search regression are complete. Successful live LLM verification is blocked because `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` are not configured. A screen-recorded video, publication/instructor access, and the precise coding-agent model disclosure still need completion. All mock results below are explicitly labeled; they are not successful live model calls. Nothing has been submitted to Canvas.

## 1. Project access and startup

- Existing private repository: [ben-randall1/IST-402-assignment-1](https://github.com/ben-randall1/IST-402-assignment-1).
- Local Part 2 branch: `codex/assignment-2-part-2`.
- Assessed implementation commit: `54034472debb1ab43c84a50efbc0ae56102c02ac` (local checkpoint; not yet published).
- Startup/configuration: [README](../README.md). Responsibilities and verification rules: [AGENTS.md](../AGENTS.md).
- The prior report is preserved in [docs/part-1-report.md](../docs/part-1-report.md).

Run from the project root:

```sh
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
# In a second terminal:
npm --prefix frontend run dev
```

Open `http://127.0.0.1:5173/`. Existing dependencies were checked; Part 2 installed none. A fresh machine must follow the README's dependency-check and student-approval procedure before installation.

Keep `GEOAPIFY_API_KEY`, `OPENROUTER_API_KEY`, and `OPENROUTER_MODEL` in the ignored root `.env`. The model ID must identify a currently available free NVIDIA Nemotron model from the class configuration. Check the [OpenRouter model catalog](https://openrouter.ai/models?fmt=free) and [current limits](https://openrouter.ai/docs/api_reference/limits). No paid fallback is enabled. The precise application model will appear in the displayed trace after a successful live call; no model has yet been configured for this checkout.

The backend reads credentials; the browser sends only the question to `/api/chat`. Do not expose keys in `VITE_` variables, screenshots, recordings, or this report. The saved hotel database remains local and ignored. An instructor's fresh checkout must save hotels through Explore or use the explicitly synthetic fixture runner.

## 2. Research and early design

[Research notes](../docs/part-2-research.md) were written before implementation, building on Part 1's list/map and local-storage work.

- [Booking.com's AI Trip Planner](https://news.booking.com/bookingcom-launches-new-ai-trip-planner-to-enhance-travel-planning-experience) informed natural-language questions and approachable comparison. Its broader booking scope does not match this application's simulated local data. StayScout therefore labels its data and provides supporting records without a booking action.
- [OpenRouter's API](https://openrouter.ai/docs/api_reference/overview) supports backend message requests with an explicit model. Model output formats can vary, so the implementation validates JSON and rejects malformed/truncated responses. Each completed question uses two requests.
- [SQLite authorization callbacks](https://www.sqlite.org/c3ref/set_authorizer.html) and [Python sqlite3](https://docs.python.org/3/library/sqlite3.html) informed a read-only connection, table/column/function allowlists, one-statement restriction and resource limits. A SELECT prefix alone is insufficient.
- Free-model availability and quotas vary. Errors remain explicit, no paid fallback is used, and failure tests are mocked rather than exhausting quota.

[Early chatbot mockup](../docs/part-2-early-mockup.svg) was saved before implementation. It includes the question form, answer, supporting SQL/records, loading, no-match and error states. The implementation keeps the existing cream/forest design, adds example-question buttons, a collapsible evidence section, independently verified stay cards, a cancellation control, and a single-column phone layout. The assistant is a separate navigation view; existing Explore and Sample stays remain available.

## 3. Implementation and complete workflow

The existing local-storage foundation remains intact: `saved_hotels`, exact `saved_hotel_searches` ZIP associations, and `demo_hotel_nights`. Repeated saves preserve edited values; removal cascades to dependent rows. The original Assignment 1 tables and `hotel_id` joins are unchanged. Geoapify locations remain distinct from simulated nightly values.

1. Vue's [HotelChat](../frontend/src/components/HotelChat.vue) accepts a natural-language question. Its [composable](../frontend/src/composables/useHotelChat.js) manages loading, cancellation, stale requests, answer, no-match and failure states.
2. FastAPI's `/api/chat` validates a 1–1,200-character question. [backend/chat.py](../backend/chat.py) sends it with the relevant schema and query rules to the configured OpenRouter model.
3. The model proposes SQL and optional stay dates/room count. The backend validates it and executes only allowed reads over the three local tables. The model never accesses SQLite directly. Writes, legacy-table reads, schema reads, unsafe functions, multiple statements and recursive queries are rejected.
4. Retrieval is bounded to 50 records and 60 KB of JSON, with an execution budget. For stays, the backend independently verifies every requested night and room count in a consistent read snapshot and recalculates totals from stored cents. Checkout is excluded; missing nights do not qualify.
5. A second model request receives the original question and exact limited records. It must give a grounded answer with valid record citations. Vue displays escaped text, simulated-data labels, totals, and expandable SQL/records/model provenance. Empty retrieval is distinct from a failed request.

The application is implemented for this full pipeline, but successful live model execution remains unverified until credentials/model are configured.

## 4. Demonstrated fixed workflow — mocked model, real SQLite and frontend

[Fixed JSON fixture](../docs/fixtures/part-2-hotels.json), [complete trace](../docs/evidence/part-2-mock-workflow.json), and [browser screenshot](../docs/evidence/part-2-mock-answer.png). Names, IDs, locations, rates and room counts in this fixture are synthetic. Both model responses are deterministic mocks; query checking, SQLite retrieval, recalculation, HTTP route and Vue rendering are real.

**Question:** “Which saved hotels in ZIP 16802 have a room from October 10 to October 12, 2026, for under $250 total? Compare the total costs.”

**Proposed SQL:**

```sql
SELECT h.hotel_id, h.name, h.address,
       SUM(n.nightly_rate_cents) AS total_cost_cents
FROM saved_hotels h
JOIN demo_hotel_nights n ON n.hotel_id = h.hotel_id
WHERE EXISTS (
  SELECT 1 FROM saved_hotel_searches s
  WHERE s.hotel_id = h.hotel_id AND s.zip_code = '16802'
)
AND n.stay_date >= '2026-10-10' AND n.stay_date < '2026-10-12'
GROUP BY h.hotel_id
HAVING COUNT(DISTINCT n.stay_date) = 2
   AND MIN(n.rooms_available) >= 1
   AND SUM(n.nightly_rate_cents) < 25000
ORDER BY total_cost_cents, h.hotel_id LIMIT 50
```

**Retrieved and verified records:**

| Hotel | October 10 | October 11 | Two-night total | Minimum rooms |
| --- | --- | --- | --- | --- |
| Pine House (fixture), `fixture-pine` | $90 / 3 rooms | $110 / 2 rooms | $200 | 2 |
| Elm Court (fixture), `fixture-elm` | $120 / 2 rooms | $120 / 1 room | $240 | 1 |

The mock answer displayed Pine as the cheaper option, a $40 saving, the dates, both totals, availability across both nights, and simulated-data limitations. Pine's expensive, sold-out October 12 row was correctly excluded because it is checkout. Missing Night and Sold Out fixture hotels did not qualify. The exact second-request records, answer and citations are in the trace.

**No-match case:** October 20–22 produced no records; the second mock request explained missing local dates and suggested changing dates or saving more hotels. It did not report a provider failure as an empty result.

**Rejected-query case:** a mock model proposed `DELETE FROM saved_hotels`. The backend returned 422 before the second model request, and the database bytes remained unchanged. The evidence also includes a mocked 429 response.

Repeat with `python3 -m backend.verify_part2`. For browser inspection, stop the normal backend and run `python3 -m backend.verify_part2 --serve` with the normal frontend. It uses a temporary database and visibly labeled mock responses. Stop the fixture server before returning to the normal backend.

## 5. Verification record

[Full expected-versus-observed record](../docs/part-2-verification.md).

| Input/action | Expected | Observed October 8 |
| --- | --- | --- |
| Backend automated suite | New workflow plus legacy regressions pass | **45 passed**. [Output](../docs/evidence/part-2-backend-tests.txt). |
| Frontend automated suite and production build | Correct state handling and valid build | **14 passed; build passed**. [Tests](../docs/evidence/part-2-frontend-tests.txt), [build](../docs/evidence/part-2-production-build.txt). |
| Fixed comparison / no match / rejected query | Accurate retrieved totals; honest empty state; no write | Passed through real route/SQLite with mocked model, and verified in browser. |
| Missing/sold-out nights, incorrect SQL total, two rooms | Check complete stay and recalculate | Invalid stays excluded; $200/$240 corrected totals; two rooms at Pine totaled $400. |
| Unsafe reads/writes, malformed SQL/output, timeout/network/429 | Bounded, credential-safe failure | Passed mocked tests; not empty success. |
| Keyboard submission / 390 × 844 display | Usable controls; no horizontal overflow | Passed; document and viewport width both 390. [Mobile](../docs/evidence/part-2-mobile.png). |
| **Live Geoapify ZIP 16802** | Exact location, shared map/list | **21 hotels** at approximately 3:49 PM Eastern; Nittany list selection and Scholar keyboard marker selection synchronized. |
| Save two real locations, restart backend and reload browser | Local persistence | Nittany Lion Inn and Scholar Hotel State College retained five simulated $100/20-room nights each. [Snapshot](../docs/evidence/part-2-local-16802-2026-10-08.json). |
| Sample stays → Harbor | Original sample behavior | 2 stays, each $300; isolated booking CRUD/restart regression passed. |
| Normal assistant without key/model | Explicit missing configuration | Correct 503 and browser error. [Screenshot](../docs/evidence/part-2-missing-configuration.png). |
| Successful live LLM workflow | Two real model calls and grounded answer | **Not run; configuration missing.** |

Corrections: the final SQL gate uses SQLite authorization rather than relying on a SELECT prefix; backend verification replaces unreliable generated stay arithmetic. Malformed provider-choice objects now fail safely. Browser full-page stitching artifacts were replaced with readable viewport screenshots. No additional packages were installed. Credential scan passed; `.env` and the database are ignored.

## 6. Screen-recorded demonstration

**Video URL: PENDING.** [Recording outline](../docs/part-2-demo-script.md).

The required recording must show the running normal application, a successful live question, model-proposed SQL, retrieved records, answer, no-match/insufficient-data behavior, and explicitly mocked query rejection. The outline and screenshots are not substitutes for the required screen-recorded live demonstration.

## 7. AI disclosure and evidence

**Coding tool:** OpenAI Codex desktop, GPT-6-based agent. The exact runtime model identifier was not exposed in the agent's session metadata; the student must confirm it from the model picker before submission. Codex performed requirements review, official-source research, early mockup, implementation, tests, browser verification and report drafting. No subagents were used.

**Application provider:** OpenRouter, configured to accept only a free NVIDIA Nemotron model. Exact model ID and successful live use remain pending. **Test responses:** deterministic mocks, not live AI-generated results.

[Selected prompts and revised approaches](../prompts/assignment-2-part-2-evidence.md) link the request, implementation, tests and decisions. [Full application prompts and schema](../backend/chat.py) are committed for inspection.

## 8. Limitations and remaining submission requirements

SQL authorization prevents forbidden operations, not every misunderstanding of natural language. The backend verifies complete stays and numerical totals, but cannot prove arbitrary model prose or intent interpretation. Review the visible records. The assistant has no conversation memory; include full constraints each time. It only knows the saved local subset and simulated nightly rows. It cannot infer taxes, fees, amenities, ratings, real inventory, or bookings. Canceling frontend waiting does not retract a request already accepted by the provider.

Before submission:

1. Configure the class OpenRouter key/model locally and verify a real successful two-call comparison and no-match case. Save the actual trace and compare it against the stored records.
2. Record the required screen demo and add its instructor-accessible URL.
3. Confirm the coding-agent model, publish the assessed Part 2 checkpoint and report, and verify instructor access to the private repository and every linked artifact. These local relative links will resolve when the files are published together; they are not yet instructor-accessible evidence.
4. Review this report and then upload it to the Part 2 Canvas assignment. Do not present the current draft as complete.
