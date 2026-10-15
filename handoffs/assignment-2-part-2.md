# Assignment 2.2 handoff — October 8, 2026

## Current status

Implementation and offline/browser verification are complete. Live LLM verification is blocked by missing `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` in root `.env`. The student was asked to add them locally, without pasting credentials into chat. The normal app returns a clear configuration error. No successful live LLM call, demo recording, publication or Canvas submission is claimed.

Branch: `codex/assignment-2-part-2`, based on the local-storage checkpoint `ef05687`. Assessed implementation: `54034472debb1ab43c84a50efbc0ae56102c02ac`. Root `report.md` is now the Part 2 report with explicit pending items; the old report is preserved in `docs/part-1-report.md`.

## Implemented

- Backend-only free OpenRouter Nemotron integration using existing httpx; two requests around validated SQL retrieval.
- Read-only SQLite URI, query-only mode, authorizer restricting three local tables/columns/functions, one statement, no recursion, bounded rows/output/computation.
- Independent full-stay validation: checkout excluded, missing nights unavailable, room count checked every night, totals recomputed from authoritative cents.
- Separate Ask StayScout view with question examples, loading/cancel, answer, no-match, error/retry, escaped content, record citations and visible proposed SQL/records/model trace.
- Explicit temporary-database fixture runner and full expected/observed documentation, research, pre-implementation SVG mockup, AI log and recording outline.
- No dependencies installed. No changes to CSV joins, Geoapify contract, local-first logic, local storage schema, or Assignment 1 sample booking implementation.

## Verified

45 backend tests, 14 frontend tests, production build, fixture workflow runner, whitespace and credential checks passed. Includes legacy regressions, denied writes and legacy reads, no-match, multi-night and multi-room checks, malformed/timeout/network/rate-limit mocks. `docs/evidence/part-2-mock-workflow.json` is explicitly mocked and verifies unchanged database bytes after a rejected DELETE.

Browser: keyboard form submission; mock $200/$240 comparison; no-match; rejected-query error; trace expansion; 390×844 layout with no horizontal overflow. Screenshots are saved in docs/evidence.

Live Geoapify regression: ZIP 16802 on October 8 at approximately 3:49 PM Eastern returned 21 hotels. List-to-map and Enter-on-marker selection passed. Saved **Nittany Lion Inn** and **Scholar Hotel State College** through the live UI. They remain in ignored `data/stayscout.db` with five default simulated $100/20-room nights (Oct 10–14), ready for a real chatbot demo. Actual backend restart plus browser reload retained both hotels. Sample Harbor search returned two $300 simulated stays. Fixture tests used temporary databases and did not contaminate working storage.

## Running services and next steps

Normal backend: `python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`; frontend: `npm --prefix frontend run dev`. The offline fixture server has been stopped. Browser localhost tab is retained, showing the real missing-configuration state.

1. Once key/model are configured, run the live comparison and no-match cases through the normal backend. Read configuration without printing secret values. The backend rereads .env per request. Ensure the configured class Nemotron model is currently available; no paid fallback.
2. Save live traces separately, update report/verification/handoff honestly, and record the required screen demo. Do not pass the offline mock trace off as live.
3. Confirm exact coding-agent model identifier in the UI; it was not exposed to the agent. Confirm instructor access and publish Part 2 only with appropriate authorization. Earlier publication authorization was specifically for codex/assignment-2-part-1; no Part 2 push was performed.
4. Submission remains pending. `docs/part-2-demo-script.md` gives the recording sequence. The separate in-class DB Browser manual checklist remains student work and is not claimed complete.
