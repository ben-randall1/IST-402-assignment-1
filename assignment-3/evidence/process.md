# Curated design evidence · October 15, 2026

## Request and requirements

Student: “Okay, now time to work on the next part of the assignment.”

The open Canvas submission identified Assignment 3.1, due October 15. The overview specifies research/design at this milestone, not a working app. The agent read it in the signed-in browser, including the R/D table, technical expectations, fictional-testing boundary, all three milestones and Section 8. This corrected the initial possibility that the next task extended the hotel chatbot. It is a separate mental-health skills design.

The agent asked an optional preference question about skill/name and proceeded with the stated provisional choice, “A little space,” paced breathing first and optional STOP later. This is a design proposal, not a student-authored clinical preference.

## Environment check

Observed October 15: Python 3.11.5, FastAPI 0.116.1, uvicorn 0.35.0, httpx 0.28.1, python-dotenv 1.1.1; Node 22.19.0, Vue 3.5.42, Vite 7.3.6, Leaflet 1.9.4. No install command was run. `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` were checked for presence only and were missing. No secret values were printed. Part 3.1 does not require these credentials.

The working tree was clean at start on `codex/assignment-2-part-2`, commit `7ee6707`. The hotel implementation is the reuse reference, not evidence of a successful live LLM conversation.

## Selected decisions and revised approaches

| Prompt/constraint or considered approach | Artifact / resulting decision | Evidence boundary |
| --- | --- | --- |
| Course: D1 gives no reliable distress detector. | [Design](../design.md): explicit “Less on screen” rather than inference from emotion, typing or time. | Proposed interaction, not validated distress adaptation. |
| Course: preserve steps, <=90 seconds including application delays. | [Timing plan](../technical-design.md): six local 4–6 rounds, no model delay inside the sequence. | Arithmetic checked; runtime duration not yet measured. |
| Considered open-ended supportive generated text. | Revised to bounded model selection of reviewed orientation IDs and enabled skill suggestions. The application controls all skill and safety copy. | Trades conversational range for inspectable behavior; model contribution still requires live testing. |
| Considered adapting the hotel RAG query pipeline. | Parameterized retrieval of fixed skills/current conversation/explicit preference; no model SQL and a separate DB. | Reuses architectural patterns without sharing hotel records. |
| Course: personalization without configuration burden, while preserving control. | One optional remember action and transparent usual-skill offer; no auto-start or inferred benefit. | Preference/cascade model tested in schema experiment only. |
| Public VA legacy URL was unavailable. | Research uses the accessible current official listing and interface overview. | No claim to have tested the native VA app. |

## Planned checks and observations

The script `check_design.py` and its [output](design-checks.txt) establish document/link coherence, SVG validity, schema constraints, reopening/cascades and timing arithmetic in isolation. [Browser review](browser-review.md) records observed storyboard behavior and screenshots. They do not establish the future Vue/FastAPI runtime, therapeutic safety or clinical effectiveness.

The prototype's “mocked model” screens have no provider call; its history is a fixed fictional fixture in page memory. Resource buttons are inert, and no crisis service is contacted. Later live model checks must be recorded separately.
