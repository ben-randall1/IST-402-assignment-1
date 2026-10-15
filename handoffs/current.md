# Assignment 3.1 handoff — October 15, 2026

## Scope and current state

The student's next-part request points to Canvas Assignment 3.1 (18506998), due October 15 at 11:59 PM Eastern. Read the overview at https://psu.instructure.com/courses/2484533/pages/assignment-3-overview-mental-health-skills-application. This milestone is Research and Design; no working app is required. Parts 3.2 and 3.3 are due October 22/29.

Created the separate `assignment-3/` design package for **A little space**: paced breathing first (6 × 4-second inhale + 6-second exhale), optional STOP later. The optional preference question received no answer during this work; the name/skill remain the agent's stated proposal, not an asserted student preference.

Branch: `codex/assignment-3-part-1`. Assessed design checkpoint: `3f99fcf06482c87ea9df8f2d9dfb50e27dd5a688`. Root `report.md` is the new Part 3.1 report. Previous Assignment 2 report/handoff preserved in `docs/assignment-2-part-2-report.md` and `handoffs/assignment-2-part-2.md`. Existing Vue/FastAPI hotel runtime is unchanged.

## Artifacts and decisions

- `assignment-3/README.md`, scoped AGENTS, research notes, design rationale/flow, annotated SVG storyboard, static clickable screen walkthrough, technical/model/data contracts, proposed SQLite schema, verification plan and evidence.
- Every R1–R4/D1–D6 finding mapped to a concrete decision, tradeoff and planned check.
- Simplification is chosen explicitly; no distress inference. Timing/steps and persistent crisis/exit controls belong to the application, not the model.
- Model selects reviewed orientation IDs using bounded current-session context and an explicit preference; no invented therapeutic advice or generated SQL. Live model contribution is future work, with no credentials configured today.
- One optional usual-skill action; no auto-start, streaks, benefit scores or mandatory disclosure. History/transcript and deletion are explicit.
- Fictional-scenario localhost coursework only. Do not offer/deploy as a mental-health support service. Verified U.S. contact information is in technical-design.md; preview actions are inert and no service was contacted.
- `AI-USE.md` records GPT-6 family and unavailable exact identifier; no subagents. Selected revised approaches documented.

## Verified October 15

`python3 assignment-3/check_design.py` passed document links, SVG validity, study-code mapping, absence of network/persistence in the walkthrough, 60-second schedule arithmetic, and isolated proposed-schema constraints/persistence/cascades. Output in assignment-3/evidence/design-checks.txt. First run caught the not-yet-written browser-review artifact; final checks passed after it was added with actual observations.

Browser: support and leave visible across all 12 static screens; support panel opened from each; support during inhale then Escape returned paused; keyboard Start worked; user-selected simplification and usual offer did not auto-start; 390×844 viewport had no horizontal overflow. Screenshots and JSON checks saved. Shared header made sticky during design review. This is storyboard behavior, not the future app's runtime, measured timing, clinical effectiveness, model or session UI.

No new dependency installed. Installed Python/Vue/backend versions inspected and recorded in evidence/process.md. No Vue build or backend rerun for untouched runtime source; no live ZIP retest relevant to this new design. Prior Assignment 2 verification remains separately dated October 8.

## Next actions

1. Student reviews the design and name/skill choice. Publish the concrete Part 3.1 design branch only with authorization covering this branch and confirm instructor access to the private repository; earlier publication approval covered Assignment 2.1 specifically. No remote push or Canvas submission performed in this session.
2. Upload root report.md to Assignment 3.1 only after accessible links are confirmed. It already identifies the assessed local design checkpoint and distinguishes planned/observed evidence.
3. For Part 3.2, follow assignment-3/README.md and AGENTS.md. Keep future frontend/backend/SQLite separate from hotel data. Do environment/approval checks before installing anything. Implement and verify the full breathing path before extending STOP.
4. Part 3.3 plan already includes 15 fictional scenarios and three invariants, but no future runtime/live-model result has been claimed.

Static design server: `python3 -m http.server 5184 --bind 127.0.0.1 --directory assignment-3`. Preview at http://127.0.0.1:5184/prototype.html. No runtime skills, provider requests or persistence in that page. The preview tab is retained for review.
