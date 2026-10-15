# Verification and evaluation plan

## Milestone boundary

Part 3.1 establishes design decisions, links between findings and decisions, an annotated sketch, a clickable storyboard, proposed contracts, and a schema experiment. It does not establish a running Vue/FastAPI app, clinical safety, effectiveness, measured exercise duration, live-model behavior, or production privacy. Runtime scenarios below are planned until explicitly observed in later evidence.

Actual October 15 observations will be recorded in [the design check output](evidence/design-checks.txt) and [browser review](evidence/browser-review.md). `python3 assignment-3/check_design.py` checks local artifact links and SVG syntax, the proposed SQL schema in a temporary database, foreign-key isolation/cascade behavior, message ordering, and the 60-second schedule arithmetic. It never opens the hotel database or calls a model. No new dependencies are needed.

No production Vue build or backend regression rerun is required for this documentation/static-storyboard change: existing runtime source is untouched. Those checks remain required when implementation begins. No fresh live ZIP search is relevant to Assignment 3; the last Assignment 2 observation remains explicitly dated October 8 rather than relabeled October 15.

## Fifteen fictional scenarios for Parts 3.2/3.3

All rows below are **planned, not run against an application**. Text represents role-play, not a real person reporting distress. Default model replies are saved mocks; repeat a small selection live only after credential configuration and with a recorded call budget (at most 50 calls for a peer session).

| ID | Fictional input / action | Expected observable behavior | Evidence to capture |
| --- | --- | --- | --- |
| F01 | Alex opens the app and chooses breathing without typing | Direct ready screen; start remains an explicit action | Click path and no model request |
| F02 | Alex asks “What do the four and six mean?” | Model selects reviewed explanation; fixed sequence unchanged | Request context, validated ID and displayed canonical answer |
| F03 | Alex chooses Less on screen before starting | Examples/chat hidden; choice, leave and support remain | Standard/simple screen comparison |
| F04 | Alex completes six breathing cycles | Inhale 4/exhale 6; ~60 seconds planned, <=90 actual active duration | Monotonic timing log plus recording |
| F05 | Alex stops during inhale | Immediate neutral exit; no reason or score demanded | State/DB status and screenshot |
| F06 | Alex pauses mid-exhale, waits, then resumes | No progress while paused; explicit replay of interrupted round; time separated | Timeline and saved progress |
| F07 | Alex backgrounds and reloads an active session | Pause/interrupted record; never automatic resume | Lifecycle recording and SQLite inspection |
| F08 | Mock provider times out or returns 429 | Fixed choices, stop and support remain; no fabricated model answer | Mock response and UI/error code |
| F09 | Mock provider returns an unknown response ID or therapeutic free text | Contract rejected; raw content never displayed | Validator assertion and escaped UI check |
| F10 | Alex sends the fictional line “I may hurt myself tonight” | Fixed support invitation/panel; no generation required; no monitoring claim | Rule result, model-call count zero |
| F11 | Alex quotes/negates a crisis phrase; another case uses a euphemism | Document possible false positive/miss; manual support always available | Expected-vs-observed false-positive/miss notes |
| F12 | Alex saves breathing as usual, restarts, then chooses another option/clears it | Offer remembers explicit choice only; override/clear works; no auto-start | Preference row before/after and entry screen |
| F13 | Alex reviews history and deletes the session used for usual | Transcript available on demand; delete cascades to messages and preference | SQLite before/after in temporary fixture |
| F14 | Alex uses keyboard, 200% zoom and reduced motion | Focus/controls usable; static labels carry pace; support/stop visible | Keyboard observations, viewport/zoom screenshots |
| F15 | Storage save fails while a stale model response arrives after Stop | Clear unsaved warning; late answer ignored; local skill/support work | Injected failures and state/revision trace |

F02/F10/F11 are candidates for a small future live-model sample; F10's application bypass must remain deterministic and use zero calls. Repeat F02 with paraphrases and ordinary harmless contexts. Model variation is assessed as intent selection, not clinical quality. If no live configuration is available, say so; do not present mocks as live.

## Three cross-case behavior checks

1. **Independent safety and exit:** From every screen, including model/storage failure and the active skill, the visible support control opens bundled information and Stop/Leave remains usable. Verify with network unavailable and model calls disabled; do not dial/message a service.
2. **Application-controlled sequence and duration:** Inputs, model outputs, late responses and remembered preferences cannot change skill steps, start automatically, or insert waits. Measure the normal active flow and interruption accounting separately; do not subtract ordinary application delays to meet 90 seconds.
3. **Explicit, reviewable memory:** Only deliberate preference actions influence the next usual-skill offer. Restart preserves intended session/message records, deletion cascades, and neither old transcripts nor completion are treated as evidence of benefit.

## Later evidence requirements

Part 3.2 needs a coherent working end-to-end demonstration, actual SQLite/browser inspection and measured timing. Part 3.3 adds at least 15 scenario observations, all three behavior checks, limited live variation, a surprising finding, an untested limitation, clean-checkout verification, finished demo, and a failure-analysis screencast explaining a relevant generated code section. This milestone does not manufacture those later observations or require an early demo video that the Part 3.1 brief does not request.
