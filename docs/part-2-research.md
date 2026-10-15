# Part 2 research — October 8, 2026, before implementation

The October 1 revision requires two LLM calls around checked SQL retrieval, building on the existing local-storage tutorial. Source: [assignment overview](https://psu.instructure.com/courses/2484533/pages/assignment-2-overview-hotel-discovery-with-public-apis).

| Source consulted | Useful pattern / limitation | Decision |
| --- | --- | --- |
| [Booking.com AI Trip Planner announcement](https://news.booking.com/bookingcom-launches-new-ai-trip-planner-to-enhance-travel-planning-experience) | Natural-language planning makes comparison approachable. Its broader travel and booking scope exceeds our local classroom inventory. | Offer example questions, a plain-language answer, and transparent supporting records. Do not imply a reservation or real inventory. |
| [OpenRouter API reference](https://openrouter.ai/docs/api_reference/overview) | A backend HTTP POST accepts messages and an explicit model ID. Models differ in output-format support. | Reuse installed httpx; require JSON in the first prompt and validate it independently. Keep the key and both requests on the backend. |
| [OpenRouter free models](https://openrouter.ai/collections/free-models/) and [limits](https://openrouter.ai/docs/api_reference/limits) | Free model availability and quotas can change; free requests have per-minute and daily limits. | Require a configurable free NVIDIA Nemotron model ID. No paid fallback, retries, or quota-exhaustion experiments. Mock failures. Each successful question uses two requests. |
| [SQLite authorizer](https://www.sqlite.org/c3ref/set_authorizer.html) and [Python sqlite3](https://docs.python.org/3/library/sqlite3.html) | SQLite can reject unauthorized operations at statement preparation. A SELECT prefix alone does not constrain table access or expensive expressions. | Use a read-only connection, query-only mode, table/column/function allowlists, one statement, a progress budget, and bounded rows/output. |

The answer must use only retrieved records. Prices and rooms are simulated. For stays, checkout is excluded; every requested night must exist and have enough rooms. SQL safety does not prove that a model understood the question, so expose the proposal and records and verify known comparisons against fixed expectations.

No new package is proposed. Environment checked: Python FastAPI 0.116.1, httpx 0.28.1, pydantic 2.13.5, uvicorn 0.35.0; Node 22.19.0; installed Vue 3.5.42, Vite 7.3.6, Leaflet 1.9.4.
