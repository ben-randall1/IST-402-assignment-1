# Assignment 3.1 — Research and Design

**Student:** Ben Randall

**Course:** IST 402, Section 003

**Project:** A little space

**Milestone date:** October 15, 2026

**Status:** The Part 3.1 design package is published in a public repository. Anonymous access to the repository and branch was verified on October 15, 2026. A working application, runtime timing measurements and live-model demonstration belong to later milestones and are not claimed here. Nothing has been submitted to Canvas.

## 1. Project access and submitted version

Repository: [ben-randall1/IST-402-assignment-1](https://github.com/ben-randall1/IST-402-assignment-1).

Design branch: [codex/assignment-3-part-1](https://github.com/ben-randall1/IST-402-assignment-1/tree/codex/assignment-3-part-1).

Assessed published design checkpoint: [744fca701d4446db1ea0c7f4a9a4565954ce587c](https://github.com/ben-randall1/IST-402-assignment-1/commit/744fca701d4446db1ea0c7f4a9a4565954ce587c). Its file tree exactly matches the reviewed local snapshot. Publication used the connected GitHub account after the saved Git credential was rejected; the original local history is preserved on a local backup branch.

The new project is organized under `assignment-3/`, separate from the existing hotel application. [Project README](https://github.com/ben-randall1/IST-402-assignment-1/blob/744fca701d4446db1ea0c7f4a9a4565954ce587c/assignment-3/README.md) explains the design artifacts and review commands. [Agent guidance](https://github.com/ben-randall1/IST-402-assignment-1/blob/744fca701d4446db1ea0c7f4a9a4565954ce587c/assignment-3/AGENTS.md) records the implementation boundaries. The previous submission report is preserved in [docs/assignment-2-part-2-report.md](https://github.com/ben-randall1/IST-402-assignment-1/blob/744fca701d4446db1ea0c7f4a9a4565954ce587c/docs/assignment-2-part-2-report.md).

Review the static walkthrough locally with no dependency installation or credentials:

```sh
python3 assignment-3/check_design.py
python3 -m http.server 5184 --bind 127.0.0.1 --directory assignment-3
```

Open `http://127.0.0.1:5184/prototype.html`. This is a clickable storyboard with fictional screens, no running breathing timer, provider calls or saved user data. The later application will use Vue in its `frontend/`, FastAPI in its `backend/`, and a separate SQLite database. Future run commands will be documented after implementation.

## 2. Proposal, main experience and research rationale

A little space supports a short skill that someone deliberately chooses, can leave without explanation, and can complete without typing. The first working scope is **paced breathing: inhale for four, exhale for six, repeated six times**. The model provides brief orientation outside the exercise. **STOP** is an optional later second choice, preserving its four steps: stop, step back, observe internally/externally, proceed mindfully. Grounding and cognitive reframing are outside the first working scope to keep it coherent and reduce required disclosure.

This is a coursework prototype for fictional role-play on localhost. It does not diagnose, provide therapy, promise benefit or imply monitoring. It will not be deployed or offered to someone in distress.

[Full research notes](https://github.com/ben-randall1/IST-402-assignment-1/blob/744fca701d4446db1ea0c7f4a9a4565954ce587c/assignment-3/research.md) use the [assignment overview's study summary](https://psu.instructure.com/courses/2484533/pages/assignment-3-overview-mental-health-skills-application) as the primary research source. The reported sample and coded mentions motivate interface decisions; they are not evidence of clinical effectiveness. Additional public sources were inspected for interaction/engineering ideas: [Headspace's short breathing example](https://www.headspace.com/meditation/breathing-exercises), [VA PTSD Coach documentation](https://mobile.va.gov/app/ptsd-coach), [W3C motion guidance](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html), and [MDN elapsed-time documentation](https://developer.mozilla.org/en-US/docs/Web/API/Performance/now). These were documentation reviews, not logged-in app tests or clinical comparisons.

| Findings | Decision and tradeoff |
| --- | --- |
| R1: brief skills | Six 10-second rounds, locally paced. Predictable timing reduces variation but gives fewer exercise choices. Actual duration still needs measurement. |
| R2 and D4: immediate, persistent safety | A visible Crisis support control opens bundled information from every screen, independent of the model. Contacting an external service still requires suitable device/connectivity. |
| R3 and R4: permission to stop and personal control | Explicit Start, Pause, Stop and Leave; no explanation, score or automatic next exercise. A remembered preference only offers a choice. |
| D1: interface contraction | The user selects Less on screen; no distress detection from typing, silence or sentiment. This preserves control but cannot automatically react to unexpressed needs. |
| D2: one action | Each exercise screen shows the current phase; safety/exit controls remain visible. Explanations and choices sit before or after the skill. |
| D3: minimize emotional cost | Chat, feedback and remembering a preference are optional. No mood rating, disclosure requirement or required completion survey. Less collected context limits personalization. |
| D5: low-burden personalization | One optional “Use this as my usual” action, transparent source, override and clear controls. No hidden inference that completion means benefit. |
| D6: low-stimulus, neutral presentation | Quiet colors, restrained copy, no compulsory sound, static pacing alternative. Motion removal preserves phase/count information. |

[The design rationale](https://github.com/ben-randall1/IST-402-assignment-1/blob/744fca701d4446db1ea0c7f4a9a4565954ce587c/assignment-3/design.md) provides individual R1–R4/D1–D6 decisions, alternatives and proposed checks. The first design revision replaced inferred distress adaptation with explicit simplification, and narrowed open-ended model-generated support to reviewed orientation choices.

## 3. Early sketch and flow

- [Annotated six-screen storyboard](https://github.com/ben-randall1/IST-402-assignment-1/blob/744fca701d4446db1ea0c7f4a9a4565954ce587c/assignment-3/storyboard.svg).
- [Clickable design walkthrough](https://github.com/ben-randall1/IST-402-assignment-1/blob/744fca701d4446db1ea0c7f4a9a4565954ce587c/assignment-3/prototype.html).
- [Main flow diagram and screen contracts](https://github.com/ben-randall1/IST-402-assignment-1/blob/744fca701d4446db1ea0c7f4a9a4565954ce587c/assignment-3/design.md#main-experience).
- [Entry screenshot](https://github.com/ben-randall1/IST-402-assignment-1/blob/744fca701d4446db1ea0c7f4a9a4565954ce587c/assignment-3/evidence/design-entry.png), [single-phase sketch](https://github.com/ben-randall1/IST-402-assignment-1/blob/744fca701d4446db1ea0c7f4a9a4565954ce587c/assignment-3/evidence/design-skill.png), [support panel](https://github.com/ben-randall1/IST-402-assignment-1/blob/744fca701d4446db1ea0c7f4a9a4565954ce587c/assignment-3/evidence/design-support.png), and [phone layout](https://github.com/ben-randall1/IST-402-assignment-1/blob/744fca701d4446db1ea0c7f4a9a4565954ce587c/assignment-3/evidence/design-mobile.png).

The main path is **choose → ready → explicitly start → six local breathing rounds → neutral ending**. Optional chat can be skipped, and model failure leaves the fixed practice available. Stop leads directly to a neutral exit. Support access during a skill pauses it; returning never automatically resumes. History is separate from the active exercise.

The storyboard was prepared before application implementation. Its reviewer selector exposes twelve proposed states, including loading/failure, paused, stopped and history. Review led to a sticky shared header so crisis access and leave controls stay visible when a screen scrolls. The walkthrough intentionally has inert resource buttons so fictional tests cannot accidentally call or message a service.

**Timing plan:** six × (4 seconds inhale + 6 seconds exhale) = 60 seconds of planned instruction. Measure from the first displayed instruction through the final exhale; ordinary rendering/scheduling delays count toward the <=90-second intended duration. No model requests or storage waits belong inside that sequence. Entry/setup is estimated separately at 10–25 seconds, plus optional message wait/reading. Those are assumptions, not measured observations. User-chosen pauses, backgrounding and support time are tracked separately; resuming repeats the interrupted round with replay reported explicitly. The timer never forces exit or another exercise.

## 4. Model role, persistence and safety plan

[Technical design](https://github.com/ben-randall1/IST-402-assignment-1/blob/744fca701d4446db1ea0c7f4a9a4565954ce587c/assignment-3/technical-design.md) specifies the proposed model contract, context, routes, resource copy, failure handling and timer plan. [Proposed SQLite schema](https://github.com/ben-randall1/IST-402-assignment-1/blob/744fca701d4446db1ea0c7f4a9a4565954ce587c/assignment-3/schema.sql) is an isolated schema experiment.

The model interprets an optional fictional message using fixed enabled-skill context, the last four messages from the current session and an explicit usual-skill preference. It returns a reviewed `response_id` and optional enabled skill ID. The application renders the corresponding approved wording. For example, a question about counts selects `explain_breathing`. This adds natural-language intent handling while keeping therapeutic content bounded. Arbitrary advice, unknown responses, new steps and automatic routing are rejected. A limitation is reduced conversational range; unsupported requests receive a scope response. Live testing must establish whether this contribution is useful.

The prior backend's free OpenRouter Nemotron pattern is the first provider candidate. Neither LLM key nor exact model is configured today; a current model availability/configuration check is needed for Part 3.2. The proposed request has an eight-second timeout, no automatic retry and no place inside the timed skill. Routine tests use labeled mocks.

SQLite will save versioned fixed skills; sessions with neutral outcomes, timestamps and progress; ordered fictional conversation messages and response provenance; and at most one explicitly chosen usual-skill preference. History shows date/skill/outcome first and opens transcript details only on request. Parameterized retrieval replaces model-generated SQL. Old transcripts are not automatically sent to the provider. Deleting a source session removes its messages and related usual choice. Local storage is unencrypted; provider processing is separate from local history deletion. No real health information, names, diagnoses or analytics are requested.

A static, region-labeled crisis-information panel remains available during every state and failure. Verified U.S. resource routes are documented in the technical design; no service was contacted. A conservative phrase rule may additionally show that same panel for explicit crisis-related fictional text and bypass model generation. Its false positives and misses are acknowledged; no-match never establishes safety. The support route always works independently of detection, generation or successful saving.

Reuse is limited to architecture and verification patterns from the hotel project: Vue request state, FastAPI validation/safe errors, SQLite transactions and fixture tests. Hotel tables, map, generated SQL execution and booking logic are not part of the new application. Prior missing live-hotel-chatbot verification is not retroactively claimed complete.

## 5. Verification and unresolved questions

[Observed design checks](https://github.com/ben-randall1/IST-402-assignment-1/blob/744fca701d4446db1ea0c7f4a9a4565954ce587c/assignment-3/evidence/design-checks.txt), [browser review](https://github.com/ben-randall1/IST-402-assignment-1/blob/744fca701d4446db1ea0c7f4a9a4565954ce587c/assignment-3/evidence/browser-review.md), [12-screen visibility checks](https://github.com/ben-randall1/IST-402-assignment-1/blob/744fca701d4446db1ea0c7f4a9a4565954ce587c/assignment-3/evidence/storyboard-screen-checks.json), and [support-opening checks](https://github.com/ben-randall1/IST-402-assignment-1/blob/744fca701d4446db1ea0c7f4a9a4565954ce587c/assignment-3/evidence/storyboard-support-checks.json) are the current evidence.

| Check | Expected | Observed October 15 |
| --- | --- | --- |
| Artifact links, SVG syntax and research mapping | Reviewable files and all ten study codes addressed | Passed design script. |
| Proposed SQLite schema in a temporary fictional DB | Valid constraints, reopening and dependent deletion | Passed; sessions/messages/preferences reopened, deletion removed dependent data and preserved fixed skill content. This is not application persistence. |
| Sequence arithmetic | Six 4–6 cycles total 60 seconds | Passed arithmetic only; runtime timing not measured. |
| Twelve walkthrough states | Support/leave remain visible and panel opens | Passed each state. |
| Support during a static inhale, then Escape | Return paused; require explicit Resume | Observed. |
| Explicit simpler mode and usual choice | Reversible simplification; offer without auto-start | Observed in page-memory simulation only. |
| Phone width 390 × 844 | No horizontal overflow; model-error controls usable | Document and viewport width both 390; panel opened. |

The first document check found the browser-review file had not yet been written; the file was added with actual observations and checks rerun. No package was installed. Existing hotel runtime source was not changed, so a Vue production build/backend regression run would not establish anything new about this design-only milestone and was not claimed.

Open questions concern no-motion pacing clarity, optional-message latency, wording of the usual-skill offer, false positives/misses in the conservative crisis rule, current model availability, and whether STOP should wait until the core flow passes. Parts 3.2/3.3 must resolve them through actual implementation evidence.

[Evaluation plan](https://github.com/ben-randall1/IST-402-assignment-1/blob/744fca701d4446db1ea0c7f4a9a4565954ce587c/assignment-3/verification.md) contains fifteen fictional scenarios and three cross-case behavior checks: independent support/exit, application-controlled timing/sequence, and explicit reviewable memory. They are **planned, not observed runtime passes**. Later work must add measured timing, browser/DB evidence, limited live-model variation, clean-checkout checks and the required finished-demo/failure-analysis recordings. A working app or recorded runtime demo is not required by Part 3.1.

## 6. AI disclosure and submission status

[AI-USE.md](https://github.com/ben-randall1/IST-402-assignment-1/blob/744fca701d4446db1ea0c7f4a9a4565954ce587c/AI-USE.md) names OpenAI Codex desktop, the GPT-6 family agent (exact runtime identifier unavailable), its roles and prior-session evidence boundaries. No subagents or live application model were used. [Curated evidence log](https://github.com/ben-randall1/IST-402-assignment-1/blob/744fca701d4446db1ea0c7f4a9a4565954ce587c/assignment-3/evidence/process.md) connects selected prompts, revised approaches, artifacts and checks; it contains no credentials, participant records or real distress disclosures.

Part 3.1 is complete and publicly published as a research/design milestone. Before Canvas upload, review the proposal. Artifact links below are absolute URLs pinned to the assessed public design commit so they also work from this standalone report. Repository visibility and branch access were verified with an anonymous GitHub API request. No deployment, clinical test, paid API call or Part 3.2 implementation is required to finish this milestone.
