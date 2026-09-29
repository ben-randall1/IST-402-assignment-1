# Assignment 2.1 AI disclosure and selected evidence

## Tool and model

OpenAI Codex desktop, **GPT-6 Astra** (`gpt-6-astra`), used for reading the assignment, reviewing the existing application, researching official documentation, preparing the early mockup, implementing Vue/FastAPI changes, creating automated checks, exercising the browser, and drafting the report. No subagents or other AI models were used in this session.

Supporting tools: shell/Python/Node, Git, browser computer use, web research, and the GitHub connector for repository metadata. They are tools used by Astra, not additional AI models. The original Assignment 1 app and in-class geocoding extension predate this session; this disclosure does not assert the model used for that prior work.

## Selected user instructions and resulting work

| Actual prompt excerpt | Result / artifact |
| --- | --- |
| “this is my first time trying astra for my vibe coding class … assigment 2 opened in the broswer … work your magic” | Read the Canvas brief and focused this implementation on the open Part 1 submission. Research and initial design were saved in [research.md](../docs/research.md) and [early-mockup.svg](../docs/early-mockup.svg). |
| “it is assignment 1 project in codex” | Confirmed the saved project path and extended a copy of its working files, including the uncommitted classroom ZIP lookup. The original folder and its Git history were preserved. Existing booking UI moved to [LegacyStays.vue](../frontend/src/components/LegacyStays.vue). |
| “Approve Leaflet installation” | After checking installed packages, ran `npm install --save-exact leaflet@1.9.4`. The version is pinned in the frontend manifest/lockfile; [AGENTS.md](../AGENTS.md) records approval and the verification loop. |

## Decisions and code evidence

- [ExternalHotel model](../backend/models.py): separates provider data from the original priced sample Hotel schema; missing fields remain null.
- [Provider controller](../backend/geoapify.py): verifies U.S. ZIP identity, requests hotels in a 5 km circle, bounds results, validates coordinates, and sanitizes failures.
- [Vue request controller](../frontend/src/composables/useHotelSearch.js): stores ZIP as text and rejects obsolete responses.
- [Leaflet view](../frontend/src/components/HotelMap.vue): same numbered hotels and selection as the list; provider text enters popup DOM through `textContent`.
- [Backend tests](../backend/test_hotel_search.py) and [frontend tests](../frontend/src/composables/useHotelSearch.test.js): repeatable wrong-location, empty, quota, missing-field, stale-response and regression evidence.

## Failed and revised approaches

The first browser attempt produced a list but an empty map because marker DOM was accessed before Leaflet received an initial map view. A console check exposed `Cannot read properties of undefined (reading 'setAttribute')`. The implementation was corrected to initialize the view first, then create marker controls. A second browser check caught Enter opening a popup without updating the card; explicit Enter/Space selection handlers corrected that behavior. Both failures and the expected-versus-observed retests are recorded in [verification.md](../docs/verification.md).

This is a selected evidence log, not a full chat transcript. The student still needs to review the work, record the required demonstration, confirm instructor access, and submit the report.
