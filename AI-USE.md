# AI use disclosure

## Assignment 3.1 · October 15, 2026

**Tool:** OpenAI Codex desktop. **Model:** GPT-6 family coding agent; exact runtime model/version identifier was not made available to the agent in this session. No more specific identifier is asserted. **Role:** read the Canvas assignment and existing repository, consult official interface/technical sources, propose a design, draft documents and diagrams, build a static clickable storyboard, run isolated schema/design checks, inspect browser behavior, and prepare the report.

No subagents were used. No therapeutic conversation, participant dataset, real patient input, or live application-model call was used. The student's request and project guidance establish the scope; student review of the design and final report remains necessary.

The proposed application model is a configurable free NVIDIA Nemotron through OpenRouter, subject to later availability/configuration checks. It is not the coding agent model. All model-response screens in the Part 3.1 walkthrough are manually specified mocks. No credentials were installed or transmitted for them.

[Curated, redacted evidence log](assignment-3/evidence/process.md) connects the request, design changes and verification. A revised approach is documented: open-ended generated support copy was narrowed to selecting reviewed orientation messages; the hotel model-generated SQL pipeline was replaced with parameterized context retrieval. Tests and screenshots are bounded to their actual observations.

## Earlier assignments

Assignment 1 and 2 evidence remains in [the existing prompt log](prompts/selected-prompts.md), [Assignment 2.1 log](prompts/assignment-2-evidence.md), and [Assignment 2.2 log](prompts/assignment-2-part-2-evidence.md). These contain their own session-specific disclosures. Their reported model identities are not reassigned to the current session. Assignment 2.2's prior missing live model verification is still unresolved; later design work does not establish it retroactively.

## Assignment 3.2 · October 22, 2026

**Tool:** OpenAI Codex desktop, GPT-6 family coding agent (exact runtime identifier unavailable). No subagents. Role: read the Canvas milestone; implement the separate Vue/FastAPI/SQLite app; reuse installed dependencies; write bounded OpenRouter classification; run temporary-database/mock HTTP and timer checks; inspect actual browser screens and SQLite; record measured duration; prepare documentation and submission. The application model is separately configured as `nvidia/nemotron-3.5-lightning:free` via OpenRouter, not the coding agent. Two production-interface live turns selected reviewed explanation/leave IDs and persisted their actual model IDs. The initial Super endpoint returned 404; Lightning first failed output validation, then succeeded after optional reasoning was disabled. See [the Part 3.2 evidence index](assignment-3/evidence/part-3-2/README.md) for separate failure/success artifacts; mocks are not evidence of successful live calls.

Selected prompt intent: implement the next coursework milestone and submit when complete. Project constraints kept the previous hotel app unchanged, fixed the breathing sequence, required independent support/exit and backend-only credentials, and prohibited unapproved dependency installations. No new packages were installed. User configuration was performed in ignored `.env`; example-key rejection prompted an explicit placeholder check. Raw secrets and provider error bodies were not captured. All test messages and records are fictional.

Revisions supported by evidence: narrowed runtime model output to exact reviewed response IDs; added separate attempt records and a revision recheck after model latency; changed the simplification view to hide optional orientation; moved the mobile support dialog's Leave control into its header. A real six-round browser run and direct SQLite inspection supplement deterministic timer/HTTP fixtures. Wider evaluation and recordings remain Part 3.3 work. The student should review the generated code and report; no claim of clinical effectiveness or user benefit is made.
