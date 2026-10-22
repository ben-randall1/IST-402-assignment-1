# Part 3.2 implementation decisions

October 22, 2026. Fictional coursework prototype, single user, localhost only.

## From the research to observed software

| Finding | Implemented decision | Tradeoff |
| --- | --- | --- |
| R1, D2 | Exactly six 4–6 rounds; one current phase, no model calls in the exercise | Only one skill is enabled. No unnecessary input during timing. |
| R2, D4 | Shared always-visible support route, bundled dialog, static contact destinations | The panel can render without the API; using external contacts still needs a suitable device/connection. |
| R3, R4 | Leave/Stop, voluntary Pause, explicit Resume; no reason or score required | A repeated interrupted round adds active time. Multiple voluntary interruptions can make a session much longer than the uninterrupted intended pace. |
| D1, D3 | Explicit reversible Less on screen hides optional orientation/examples | No distress inference. No text or emotional disclosure is required to begin. |
| D5, R4 | Explicit Save as usual / Forget; offer only, no automatic start | One additional deliberate action instead of inferring preference or benefit from completion. |
| D6 | Muted colors, neutral ending, still cue, phase words, no judgment/benefit score | A visual cue remains; broader accessibility and user testing are unfinished. |

## Responsibilities and data flow

`backend/domain.py` holds fixed versioned skill content and reviewed response text. `provider.py` owns the backend-only OpenRouter request and exact result validation. `storage.py` opens only this application's database with foreign keys enabled. `main.py` validates bounded inputs, builds parameterized current-session context, applies revision/state checks, and maps failures to HTTP statuses. No model output is SQL or rendered HTML.

Vue's `usePractice.js` owns request cancellation, a generation check, save queue and shared screen/session state. `practiceClock.js` is a network-independent monotonic timer. Views render escaped strings. `SupportPanel.vue` is bundled static information with native dialog focus containment and keyboard dismissal. The underlying screen stays paused after dismissal. The phone/text/chat links were obtained from the connected local-hotline tool; no test activated them.

SQLite uses the four original design tables plus `message_attempts`. The extra table was added to distinguish pending, failed, stale and successful attempts, and to prevent an idempotency token from spending another call. User text is committed before the provider call. A failed request retains its fictional user message and safe status code without fabricating an assistant reply. A successful validated ID produces canonical local text, saved with the actual configured model ID. Fixture replies use `fallback`, a visible mock prefix, and no live model ID.

A provider call runs outside the DB transaction. Before saving a reply, the controller checks that the session is still ready at the same revision. Starting/stopping while a call is pending invalidates it. A test uses a blocked mock provider and an actual concurrent state update: the late reply receives 409, its attempt is marked stale, and no assistant answer is saved.

## Sequence and timing

The clock derives phase from `performance.now()` elapsed time, not accumulated tick counts. It checks approximately every 100 ms and records observed callback delay. The first cue and final-screen commit are measured after Vue's next DOM update. A completed uninterrupted browser run measured 60,003 ms from first cue to final planned step, 60,004 ms active clock time, zero pause/replay, and 13,389 ms choice/setup time including an optional mock orientation interaction. A final production-bundle run after UI/reload revisions measured 60,005 ms displayed sequence / 60,003 ms active, zero pause/replay, and 364 ms setup without conversation. Timing JSON includes the actual traces; no arithmetic-only test is presented as a browser measurement.

Pause freezes planned progress. Resume explicitly repeats the partial round from inhale and records replay time; neither the pause nor support time forces an exit. Backgrounding pauses. Reload abandons any automatic resume and marks the prior saved session interrupted; an abrupt crash may lose time since the latest phase checkpoint. API restart marks active records interrupted. A completed record is a timing outcome, not evidence of benefit.

## Failure boundaries and revisions

The initial live-model attempt failed because the configuration still contained a placeholder key. This was an actual rejected request, not a successful model answer. Placeholder detection was added to configuration checks so example values are treated as missing configuration before making another request. The key itself was neither logged nor included in evidence.

Mock 429, timeout, malformed response and transport failure remain distinct failures. No automatic retry or silent paid fallback is used. A canceled client request does not guarantee provider-side cancellation; the backend revision guard prevents a delayed result from replacing an active exercise. Save failures show an unsaved warning and leave the local clock and bundled support route functional.

The first narrow-screen review showed Leave below the dialog fold. The dialog header was revised to keep Close and Leave at the top while content scrolls. The first simplification pass hid only examples; it was revised to hide the optional orientation section too, preserving all start/stop/support controls.

The valid-key Super endpoint subsequently returned provider HTTP 404. We explicitly selected catalog-listed free Nemotron 3.5 Lightning. Its first response failed validation; disabling optional reasoning for the bounded classification request was followed by a valid stop-complete response with zero reasoning tokens and zero reported cost. This supports the revised request configuration without proving the original failure's cause. Two production-interface live turns then selected `explain_breathing` and `different_choice`; reload and direct SQLite inspection showed four ordered messages and actual model IDs. See the evidence index for the failure and success artifacts.

## Scope and limits

The API has no login or account isolation. Random session IDs and loopback binding support a local single-user exercise only. SQLite is unencrypted; external processing is disclosed before Send. Local delete cannot erase provider copies. No real participant data, health record, deployment, distress classification claim, or clinical test is included.

The crisis text rule is deliberately limited: explicit substrings such as `hurt myself` trigger a fixed application response and panel without calling the model. Negation/quoting can falsely trigger it; euphemisms can be missed. The manual route is always available independent of that rule. It is not triage and no absence-of-risk claim is made.

Only paced breathing is implemented. Wider live-model variation, a full 15-scenario/three-invariant evaluation, screen-reader/zoom testing, recordings and clean-checkout verification remain Part 3.3 work. A fixed timeout can reject a slow but otherwise valid free-model reply; starting the practice does not depend on that reply.
