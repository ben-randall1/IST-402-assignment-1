# Assignment 3 implementation guidance

These instructions apply inside this design package and its future application. Repository-root instructions also apply.

- This is a fictional-scenario coursework prototype. Never offer, deploy, or recommend it as support for a real person in distress. No clinical efficacy, diagnosis, therapy, surveillance or emergency-dispatch claims.
- Part 3.1 is design only. Treat proposed routes, timing, model prompts and schema as plans until implemented and verified. Keep expected results distinct from observations.
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
