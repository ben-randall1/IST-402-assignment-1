# Part 3.2 verification evidence · October 22, 2026

All input is fictional. Actual browser observations, temporary-database tests and live-provider checks are distinguished below. None establish clinical effectiveness, distress detection, or support-service suitability.

## Observed end-to-end mock flow

On `http://127.0.0.1:5174/`, with the explicit fixture API:

| Check | Expected | Observed |
| --- | --- | --- |
| Choose and optional orientation | Choice does not auto-start; mock response labeled | Chose paced breathing, asked “Fictional: what do the counts mean?”, saw `[MOCK RESPONSE]` and canonical explanation. [Screenshot](mock-orientation.png). |
| Full exercise | Six 4–6 rounds, <=90 seconds at intended uninterrupted pace | Actual first-cue-to-final-DOM interval **60,003 ms**; active **60,004 ms**; pause/replay **0 ms**. Setup from choice through optional orientation to first cue **13,389 ms**. [Running screen](active-practice.png), [ending](completed-measurement.png), [saved timing/trace](measured-session-MOCK.json). |
| SQLite and reload | Session, ordered transcript and timing survive reload | Completed row, two messages, explicit preference row, five isolated tables and empty foreign-key violation check in [direct SQLite inspection](sqlite-inspection-MOCK.json). Reloaded browser and opened [saved history](history-after-reload.png); no automatic start. |
| Explicit preference | Offer remembered choice only after action | Clicked Save as usual, returned home, reloaded; “Your saved choice” appeared with Choose and Forget. No auto-start. Tests additionally verify absence of preference after ordinary messages and deletion cascade. |
| Model quota failure | Failure, no invented assistant answer; Start/Leave/Support remain | Sent `Fictional: mock rate limit`; saw `[MOCK FAILURE]`, retained only user text for that attempt. [Screenshot](mock-rate-limit.png), [attempt records](fixture-records-MOCK.json). Timeout/network/malformed failures are also covered by fixtures/tests. |
| Crisis-related fictional text | Application bypass, fixed panel, no generated advice | Sent `Fictional scenario: I may hurt myself tonight.`; fixed panel opened. [Support](independent-support.png). Automated test makes any model call fail an assertion and still gets a successful fixed crisis response. |
| Support while exercising | Pause immediately, stay paused after Close/Escape | Opened support during the exercise, dismissed with Escape, saw explicit Resume and Stop. [Paused screen](support-leaves-paused.png). Resume replays interrupted round; clock tests verify accounting. |
| API outage and leaving | Clock/support/leave independent of persistence | Stopped the fixture API, resumed local practice, saw unsaved checkpoint warning, opened [support without API](support-api-off.png), and used Leave to reach [neutral stopped state](stopped-api-off.png). API-off does not prove all browser networking is offline. |
| Explicit simpler view | Hide optional orientation/examples, keep essential controls | Chose Less on screen on the ready view; optional conversation disappeared while Start, Leave and Support remained. No inference from message text. |
| Narrow layout and keyboard | No horizontal overflow; keyboard support accessible | At 390×844, DOM client/scroll width both 390. Enter opened support, Tab focused the first contact without activating it, Escape closed and restored focus. The initial mobile dialog put Leave below the fold; revised header keeps Close/Leave at the top. [Initial mobile evidence](mobile-support.png); [final header](mobile-support-revised.png) was then checked in the production bundle, and its visible Leave reached the stopped view. No screen-reader/200% zoom conformance claim. |

The mock server made **zero external provider calls**. Its database is disposable. [Exported fixture records](fixture-records-MOCK.json) preserve selected fictional rows before shutdown, not a production database or a live-model result. Timing used the actual browser's monotonic clock and DOM update boundary. A 1 ms difference between active time and displayed sequence reflects their separate capture points. Browser runs can vary; no universal scheduling bound is claimed.

## Final production-bundle checks

After the simplification, dialog and reload-race revisions, `npm run preview --prefix assignment-3/frontend` served the built bundle. A second actual uninterrupted exercise measured **60,005 ms** first cue to final DOM, **60,003 ms** active, zero pause/replay, and **364 ms** choice/setup without conversation. [Production ending](production-completed.png), [SQLite timing export](production-measured-session.json). The normal API was restarted and its prior failed-request records remained; reloading a new active practice returned home and recorded an interrupted **102 ms** checkpoint. [Reload screen](reload-interrupted.png), [SQLite restart inspection](restart-inspection.json). No automatic resume occurred.

## Automated verification

Observed commands and results are preserved in [checks.txt](checks.txt). New backend tests use temporary SQLite and mocked HTTP/model results; timer tests inject time. Coverage includes bounded current-session context, reviewed-ID validation, no paid fallback, safe timeout/transport/quota/malformed failures, request idempotency, explicit memory/cascade, input/revision/time validation, restart interruption, and stale response rejection while a session starts concurrently.

The prior hotel runtime was not modified. Its 45 backend tests, 14 frontend tests and production build were also rerun. No new live ZIP lookup was needed; this work makes no fresh hotel-provider observation. The previously dated ZIP evidence stays attributed to its original assignment.

## Live model: failures, revision and successful demonstration

[Free model catalog](free-model-catalog.json) is an actual public OpenRouter API read on October 22. `nvidia/nemotron-3-super-120b-a12b:free` had zero prompt/completion pricing; that confirms catalog listing, not endpoint capacity or a successful answer.

The first actual provider attempt was rejected because the student had saved an example placeholder in `.env`. The API returned a safe failure and retained the user message without an assistant answer. An authentication-status-only check returned 401. The key value and raw error body were never captured. Configuration validation was then changed to reject example placeholders locally. The student then supplied a valid key; a status-only authentication check returned 200. The initially selected `nvidia/nemotron-3-super-120b-a12b:free` still returned provider HTTP 404, including on a minimal fictional test ([sanitized diagnostic](live-diagnostic.json)). It was explicitly replaced with catalog-listed `nvidia/nemotron-3.5-lightning:free`; no paid fallback or account-policy change occurred.

The first Lightning attempt failed the strict output contract ([saved failure](live-first-lightning-failure.json)). Optional reasoning was then explicitly disabled for this short classification task and output bounded to 512 tokens. Reasoning-budget exhaustion was a hypothesis, not established from the first raw response. A subsequent actual request returned HTTP 200 / finish `stop`, 30 completion tokens, zero reasoning tokens and reported cost 0; the validated ID was `explain_breathing` ([sanitized metadata](live-reasoning-adjustment.json)). No raw reasoning or arbitrary provider prose was stored in evidence.

The **production interface then succeeded on two actual live turns**: an explanation request selected `explain_breathing` ([screen](live-orientation.png)), and a fictional follow-up about leaving selected `different_choice` ([screen](live-follow-up.png)). The second turn used the first two current-session messages as context. Leave produced a neutral stopped session. After browser reload, [history displayed both model responses](live-history-after-reload.png). [Direct SQLite inspection](live-sqlite-session.json) confirms four ordered messages, two successful attempts, actual model IDs with source `model`, and no foreign-key violations. This is the live contribution demonstration, separate from the mock timer flow.

Eight model-generation requests were attempted across this review, including the earlier rejected placeholder request, three failed Super checks, the first invalid Lightning response, one successful adapter diagnostic and two successful UI turns. Authentication/catalog GETs are separate read-only checks. This is below the 50-call review limit; routine and future peer tests should use the explicit fixture server.

## Limits and next milestone

Only paced breathing is enabled. The broader 15-scenario/three-invariant evaluation, live variation, clean-checkout verification, full accessibility review and recordings are Part 3.3 work. The substring crisis rule may falsely match negations or miss euphemisms; manual support access does not depend on its decision. SQLite is local, unencrypted and single-user. A saved completion is not evidence of benefit. Never use real distressed participants or activate crisis contacts during tests.
