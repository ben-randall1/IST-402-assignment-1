# Assignment 3 implementation guidance

These instructions apply inside this design package and its future application. Repository-root instructions also apply.

- This is a fictional-scenario coursework prototype. Never offer, deploy, or recommend it as support for a real person in distress. No clinical efficacy, diagnosis, therapy, surveillance or emergency-dispatch claims.
- The archived Part 3.1 documents are design only. Part 3.2 runtime code is now in frontend/ and backend/. Read README.md, implementation.md and evidence/part-3-2/README.md for checked behavior; keep expected results distinct from observations.
- Keep this application's Vue code in its `frontend/`, FastAPI in its `backend/`, and SQLite file in its `data/`. Do not use or migrate the hotel database. Preserve all earlier assignments.
- Before installing anything, check the environment, explain the exact package/command, and obtain student approval. Part 3.1 requires no installation.
- Keep future credentials in the ignored repository-root `.env`; never expose keys in Vue variables, screenshots, error bodies or evidence. Default demonstrations to labeled mocks; live calls stay on the backend.
- Model: fixed versioned skill content, separate session/conversation/preferences persistence, parameterized retrieval. No model-generated SQL or model-driven changes to skill steps, timer, exit controls or safety affordances.
- Controller: validate bounded inputs, enforce session ownership for this local single-user prototype, avoid logging conversation bodies, and map transport/quota/malformed responses to safe failures. Do not let delayed responses change an exercise or a newer screen.
- View/composables: own visible state and timer transitions; views render escaped content. Crisis information and permission to stop must remain available in all states, including offline/model/storage failure, pause and history.
- Timing: six cycles of inhale 4 seconds/exhale 6 seconds, about 60 seconds plus measured local rendering delay, at most 90 seconds intended active duration. Never wait for a model mid-skill. Pauses are voluntary; the timer never forces completion or exit.
- Simplification is explicitly chosen, not inferred from distress, speed, text length, diagnosis or classifier confidence. Only offer a remembered skill; never auto-start or treat completion as benefit.
- Use fictional inputs only. Routine automated tests use fixtures. Peer tests default to mocks; if live calls are necessary, cap a session at 50 calls and switch back to mocks at the limit.
- After changes, run relevant checks and record observed outcomes in `evidence/`, `../handoffs/current.md` and `../report.md` as appropriate. Documentation-only changes do not establish a working Vue/FastAPI app.

## Part 3.2 runtime checks

- Reuse the root frontend installation through this frontend Vite configuration; no new dependency install was approved for Part 3.2.
- Normal API: `python3 -m uvicorn main:app --app-dir assignment-3/backend --host 127.0.0.1 --port 8001 --no-access-log`. Explicit disposable mocks: `python3 assignment-3/backend/fixture_server.py`; never import that runner in the normal app.
- Run `python3 -m unittest discover -s assignment-3/backend -p "test_*.py" -v`, `npm test --prefix assignment-3/frontend`, and `npm run build --prefix assignment-3/frontend`. Browser timing remains separate from fake-clock tests.
- Preserve message_attempts idempotency/failure records, revision checks around slow calls, safe errors, and no automatic retries. Keep model limits and mock/live labels explicit.
