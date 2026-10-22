# Assignment 3.2 — Working Application and Safety

**Student:** Ben Randall · **Course:** IST 402, Section 003

**Project:** A little space · **Milestone date:** October 22, 2026

**Status:** The Part 3.2 implementation and verification are complete locally, including two successful live-model turns, SQLite persistence, actual browser timing, independent crisis access, request failure and leaving. The verified source and evidence are published in the public repository at the assessed checkpoint below. Part 3.3 evaluation and recordings are not claimed.

## Repository and review access

Repository: [ben-randall1/IST-402-assignment-1](https://github.com/ben-randall1/IST-402-assignment-1). Branch: [codex/assignment-3-part-2](https://github.com/ben-randall1/IST-402-assignment-1/tree/codex/assignment-3-part-2).

**Assessed published implementation/evidence commit:** [32925c9e66b17f89663ab9e4c058439cb07405c0](https://github.com/ben-randall1/IST-402-assignment-1/commit/32925c9e66b17f89663ab9e4c058439cb07405c0). Its complete file tree matches the verified local snapshot (`62e494a596d1a29e44c8e3abd6bd553d4b3eaa66`). Anonymous verification on October 22 confirmed public repository visibility, the matching branch ref and HTTP 200 for all 14 artifact links below. A follow-up documentation commit adds these exact links; it does not change runtime source or test evidence. Earlier local history is retained privately rather than publishing administrative receipt notes.

Accessible artifacts at that immutable checkpoint:

- [Run/configuration/verification README](https://github.com/ben-randall1/IST-402-assignment-1/blob/32925c9e66b17f89663ab9e4c058439cb07405c0/assignment-3/README.md).
- [Implementation decisions and R/D tradeoffs](https://github.com/ben-randall1/IST-402-assignment-1/blob/32925c9e66b17f89663ab9e4c058439cb07405c0/assignment-3/implementation.md).
- [Expected-versus-observed evidence index](https://github.com/ben-randall1/IST-402-assignment-1/blob/32925c9e66b17f89663ab9e4c058439cb07405c0/assignment-3/evidence/part-3-2/README.md), with browser screenshots and actual database exports.
- [Actual live conversation in SQLite](https://github.com/ben-randall1/IST-402-assignment-1/blob/32925c9e66b17f89663ab9e4c058439cb07405c0/assignment-3/evidence/part-3-2/live-sqlite-session.json) and [live history after reload](https://github.com/ben-randall1/IST-402-assignment-1/blob/32925c9e66b17f89663ab9e4c058439cb07405c0/assignment-3/evidence/part-3-2/live-history-after-reload.png).
- [Measured production exercise](https://github.com/ben-randall1/IST-402-assignment-1/blob/32925c9e66b17f89663ab9e4c058439cb07405c0/assignment-3/evidence/part-3-2/production-measured-session.json) and [completion screen](https://github.com/ben-randall1/IST-402-assignment-1/blob/32925c9e66b17f89663ab9e4c058439cb07405c0/assignment-3/evidence/part-3-2/production-completed.png).
- [Executed checks](https://github.com/ben-randall1/IST-402-assignment-1/blob/32925c9e66b17f89663ab9e4c058439cb07405c0/assignment-3/evidence/part-3-2/checks.txt), [AI-use disclosure](https://github.com/ben-randall1/IST-402-assignment-1/blob/32925c9e66b17f89663ab9e4c058439cb07405c0/AI-USE.md), and [agent guidance](https://github.com/ben-randall1/IST-402-assignment-1/blob/32925c9e66b17f89663ab9e4c058439cb07405c0/assignment-3/AGENTS.md).
- [Part 3.1 report](https://github.com/ben-randall1/IST-402-assignment-1/blob/32925c9e66b17f89663ab9e4c058439cb07405c0/assignment-3/report-3.1.md), [design rationale](https://github.com/ben-randall1/IST-402-assignment-1/blob/32925c9e66b17f89663ab9e4c058439cb07405c0/assignment-3/design.md), [storyboard](https://github.com/ben-randall1/IST-402-assignment-1/blob/32925c9e66b17f89663ab9e4c058439cb07405c0/assignment-3/storyboard.svg), and [technical plan](https://github.com/ben-randall1/IST-402-assignment-1/blob/32925c9e66b17f89663ab9e4c058439cb07405c0/assignment-3/technical-design.md) retain the historical design context. Part 3.2 has no required recording; finished-demo/failure-analysis recordings remain Part 3.3 work.

Run from the repository root, in two terminals:

```sh
python3 -m uvicorn main:app --app-dir assignment-3/backend --host 127.0.0.1 --port 8001 --no-access-log
npm run dev --prefix assignment-3/frontend
```

Open `http://127.0.0.1:5174/`. This is a fictional-scenario coursework prototype on localhost, not therapy, diagnosis, a monitored service or something to rely on during distress. Do not deploy it or test it with a real person in distress. The hotel application remains separate and unchanged.

## Implemented scope and research decisions

One complete chosen skill is implemented: paced breathing, six rounds of inhale 4 seconds and exhale 6 seconds. The current phase and count carry the pace without requiring typing. Start, Pause, Resume, Stop, Leave and a still-cue alternative are explicit. Less on screen hides optional orientation and examples; it is chosen by the user rather than inferred from text or behavior. The ending is a neutral timing outcome, not a score or claim of benefit.

R1 and D2 led to a short fixed sequence with no model waits inside it. R2 and D4 led to a shared persistent crisis-support control backed by bundled frontend content. R3/R4 led to immediate stopping, no explanation requirement and no automatic resume. D1/D3 led to explicit simplification and optional conversation; no disclosure or feeling rating is needed to start. D5 led to one deliberate Save as usual action with Forget and a future offer, never automatic selection or an inferred benefit. D6 led to muted visuals, restrained motion and neutral language. These decisions give up broad skill choice and open-ended chat to preserve a coherent, predictable first version. The research findings motivate design; they do not establish clinical effectiveness.

The earlier project contributed request-state/cancellation, safe HTTP failures and temporary SQLite fixture patterns. No hotel tables, booking behavior, map, or generated-SQL pipeline were reused. The new database is `assignment-3/data/skills.db`, independently ignored. No new packages were installed; the frontend reuses the already installed root Vue/Vite packages.

## Model contribution, relevant context and memory

The normal backend uses a configured free NVIDIA Nemotron model through OpenRouter. The catalog-verified candidate is `nvidia/nemotron-3.5-lightning:free`; paid IDs are rejected and no paid fallback is selected. Each explicit Send makes at most one request; the server caps review calls at 50. Routine/peer demonstrations use the explicitly labeled temporary fixture server.

For an optional fictional orientation message, FastAPI retrieves up to four messages from that session and the explicitly saved usual preference using parameterized SQL. It supplies those records, the fixed skill/version and reviewed response library to the model. The model selects an exact response ID and optional enabled skill ID. The application validates that proposal and renders canonical local text. Unknown fields, invented instructions/skills and inconsistent preference suggestions are rejected. The model cannot change steps, timing, controls, safety access or SQL.

**Actual live result:** The production interface selected `explain_breathing` for a fictional counts question, then `different_choice` for a follow-up about leaving, using prior current-session context. Both displayed canonical reviewed text and were persisted with source `model` and `nvidia/nemotron-3.5-lightning:free`. After Leave and reload, history and direct SQLite inspection showed four ordered messages and two successful attempts.

The path also exposed real failures: an initial placeholder key was rejected, then a valid key authenticated but the original free 3 Super endpoint returned provider 404. We explicitly selected free Lightning; its first response failed contract validation. Disabling optional reasoning for short ID selection, with a 512-token maximum, was followed by a valid response with zero reasoning tokens and zero reported cost. Reasoning-budget exhaustion was a hypothesis, not a verified cause of the earlier response. No paid fallback or account privacy-setting change occurred. Eight total generation attempts, including failures/diagnostics, stayed below the review-session limit. Mock responses remain separately labeled.

SQLite stores fixed skill content, session timestamps/status/timing/progress/revision, ordered conversation text/source/model/response identifiers, explicit usual preference, and separate attempt status. Failed/stale attempts remain distinguishable from successful answers. History lists the latest 50 sessions and loads transcripts only on explicit inspection. Deletion cascades to messages/attempts and any usual choice sourced from that session. Local deletion cannot erase provider-held data. The database is unencrypted and the API is single-user localhost with no accounts.

## Actual timing, persistence and failure evidence

In the actual browser, one full six-round mock-mode run measured **60,003 ms** from the first cue's DOM update to the final planned-step DOM update, with **60,004 ms** active clock time, **0 ms** paused/replayed, and **13,389 ms** choice/setup including optional orientation. This is below the 90-second intended-pace limit and includes observed application delay. A final production-bundle check after UI/reload revisions measured **60,005 ms** first cue to final DOM, **60,003 ms** active, zero pause/replay, and **364 ms** choice/setup without conversation. Both observations are separate from arithmetic/fake-clock tests. The 1 ms capture difference is reported rather than rounded into an exact 60-second claim. Voluntary pauses/support time are tracked separately. Resume repeats a partial round and records extra active time; multiple voluntary interruptions can lengthen a session.

Direct SQLite inspection found the completed record, two ordered fictional messages, an explicit preference, the five isolated application tables and no foreign-key violations. Browser reload preserved the transcript/history without starting anything. Normal API restart preserved records; reloading an active practice returned home and marked an interrupted 102 ms checkpoint. Abrupt interruption can lose time since the last checkpoint and is not reported as completion.

A mock 429 showed a labeled failure while Start, Leave and Support remained available. Automated mocks also cover timeout, network, malformed and unknown-model-output cases. The live configuration rejection also remained a failure. Stopping the API during the loaded local exercise produced an unsaved-checkpoint warning; support still opened and Leave immediately showed the neutral stopped screen. Closing support during a running exercise left it paused with explicit Resume. No crisis contact was dialed, messaged or opened during tests.

The crisis route never depends on a model or classifier. A conservative substring rule can open the same fixed panel for explicit fictional phrases; the unit test asserts zero model calls on that branch. It can falsely match negation/quotation and miss euphemisms, and is not risk assessment. The manual route remains available independently. The app does not monitor or contact anyone for the user.

## Verification, revisions and remaining work

Executed checks: **13 backend tests**, **7 frontend timer/request tests**, and the **Vue production build** passed. The previous hotel application's **45 backend tests**, **14 frontend tests** and production build also passed. No fresh hotel ZIP call was needed; prior dated evidence is not relabeled as new. Production-bundle browser checks covered restart/history, active reload, narrow layout and keyboard support access. At 390×844 there was no horizontal overflow; Enter, Tab and Escape worked without activating contacts.

Evidence prompted revisions: an example API key was initially mistaken for configured input, so placeholders now fail locally; the initial mobile dialog left Leave below the fold, so Close/Leave moved to a sticky header; simplification initially hid only examples, so it now hides the optional orientation section. A concurrent delayed-model test confirms that starting a session invalidates the pending reply: HTTP 409, stale attempt, and no saved assistant answer.

Remaining for Part 3.3: the full 15-scenario/three-behavior-check evaluation, limited live variation, broader accessibility review, clean-checkout verification and demonstration/failure-analysis recordings. Only paced breathing is enabled. No clinical, universal timing, multi-user privacy or deployment suitability claim is made. See `AI-USE.md` and the curated evidence index for coding-agent/application-model distinctions and the redacted development record.
