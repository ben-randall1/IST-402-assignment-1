# Assignment 3.2 working application handoff · October 22, 2026

Branch: `codex/assignment-3-part-2`, based on prior public checkpoint `93183f529cde20b75bac9d5b4f8169dd207f5382`. The prior submission notes are preserved in `handoffs/assignment-3-part-1.md`; its report is archived at `assignment-3/report-3.1.md`.

Implemented a separate Vue/FastAPI/SQLite prototype in `assignment-3/`. One fixed six-round 4–6 skill, independent bundled support/leave, explicit simpler view/still cue, optional reviewed-ID model orientation, bounded current-session context, optimistic revisions and idempotent attempt records, actual timing checkpoints, transcript history, explicit usual choice and cascade deletion. Hotel runtime untouched. No dependency installation. Root `.env` remains ignored; SQLite ignored.

Observed: 13 new backend tests, seven frontend timer/request tests, new Vue build pass; 45 prior backend tests, 14 prior frontend tests and prior Vue build pass. Browser completed a full mock-mode exercise in 60,003 ms displayed-sequence / 60,004 ms active time, zero pauses, with 13,389 ms choice/setup. Reload/history and direct SQLite inspection confirm records; mock 429, deterministic crisis bypass, pause/support, keyboard/narrow screen, and support/leave with API stopped observed. Evidence is in `assignment-3/evidence/part-3-2/`.

Live verification is now complete: the student replaced the placeholder with a valid key (authentication 200). 3 Super returned provider 404; explicitly selected catalog-listed free `nvidia/nemotron-3.5-lightning:free`, no paid fallback. First Lightning output failed validation; disabling optional reasoning / bounding output to 512 tokens produced a validated response with reported zero cost. Two actual production UI turns selected explain_breathing and different_choice; reload and SQLite inspection showed four ordered messages, two successful attempts and actual model IDs. Eight generation attempts total across review, below 50. Failure and success artifacts remain separate. Credentials never printed; no account policy changed.

Final production browser run: 60,005 ms displayed sequence / 60,003 ms active, zero pause/replay, 364 ms choice/setup. Normal API restart and active browser reload confirmed retained history and interrupted 102 ms checkpoint without resume. New/revised markdown links resolve, credential-value scan found no matches in changed files, .env/SQLite ignore rules verified.

Current processes: production preview at 127.0.0.1:5174 and normal API at 127.0.0.1:8001; both use the latest source/build. The disposable fixture server was stopped. Configuration reads ignored root `.env` per request.


Public source/evidence checkpoint: `32925c9e66b17f89663ab9e4c058439cb07405c0`; its tree matches the verified local snapshot. Final report metadata links to that immutable checkpoint. Runtime source remains unchanged. Screenshots contain fictional test data only; administrative receipts and credentials are excluded from publication.
