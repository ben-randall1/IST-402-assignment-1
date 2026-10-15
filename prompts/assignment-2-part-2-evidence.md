# Part 2 AI evidence log — October 8, 2026

Tool: OpenAI Codex desktop, GPT-6-based agent. The precise runtime model identifier is not exposed in the session metadata available to the agent; the student should confirm the displayed model before submission. No subagents were used. OpenRouter/Nemotron is the implemented application provider; no successful live model call has been claimed.

## Selected prompts and decisions

- Student: “please complete part 2 of the assignment”. Codex read the current Canvas submission and overview, discovering the October 1 RAG revision. The local-storage-only scope was superseded. [Implementation](../backend/chat.py), [view](../frontend/src/components/HotelChat.vue).
- Project guidance: “Before adding a dependency, explain the exact package and installation command and obtain the student's approval.” Codex inspected installed versions and reused httpx, SQLite, Vue and Node's existing test runner; no packages were installed. [Research/environment check](../docs/part-2-research.md).
- Codex asked the student to configure `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` locally, without pasting a key into chat. Neither was configured at the last verification. Normal requests return an explicit 503; mock evidence is labeled. [Configuration and provider boundary](../backend/chat.py), [mock evidence runner](../backend/verify_part2.py).
- Query prompt excerpt: “Use exactly one SELECT statement … only the supplied tables … Missing nights are NOT available.” Answer prompt excerpt: “Use ONLY the supplied retrieved records and stay constraints.” The full committed prompts and schema are constants in [backend/chat.py](../backend/chat.py).

## Revised approaches

A keyword/prefix-only query filter would not restrict private-table reads or expensive expressions. The final implementation uses a SQLite authorizer and read-only connection with explicit table/column/function allowlists, bounded rows and computation. Model-generated totals are recalculated and missing-night candidates removed before the second request. [Adversarial and stay tests](../backend/test_chat.py).

Malformed provider choices initially could reach dictionary access without a type check. A type check and regression case now turn this into a credential-safe service failure. Full-page screenshots had stitching artifacts and were replaced with viewport screenshots. [Verification record](../docs/part-2-verification.md).

## Assistance performed

Codex researched official sources, saved the early SVG mockup before implementation, wrote the backend/frontend, fixtures and tests, performed browser verification, and drafted documentation. It did not record a demo video, publish this work, submit to Canvas, or invent successful live LLM evidence. Student review, model identification, live configuration and demonstration remain explicit submission tasks.
