# A little space · Assignment 3

**Part 3.1: research and design, October 15, 2026.** This folder is a design package for a localhost coursework prototype evaluated only with fictional scenarios. It is not a mental health service, therapy, diagnosis, or monitored support. The hotel application remains separately runnable using the repository-root README.

## Review this milestone

1. Read [the design rationale and flow](design.md), including R1–R4/D1–D6 traceability, skill timing, user control, and open questions.
2. Open [the annotated storyboard](storyboard.svg) and [clickable design walkthrough](prototype.html). The walkthrough simulates screens; it has no model, actual breathing timer, database, or clinical functionality.
3. Read [research and source notes](research.md), [model/data contracts](technical-design.md), and the [proposed SQLite schema](schema.sql).
4. Review [verification and fictional evaluation cases](verification.md), [AI disclosure](../AI-USE.md), and [selected evidence](evidence/process.md). The submission file is [report.md](../report.md).

No dependency installation, account signup, or API key is required to review Part 3.1. From the repository root:

```sh
python3 assignment-3/check_design.py
python3 -m http.server 5184 --bind 127.0.0.1 --directory assignment-3
```

Open `http://127.0.0.1:5184/prototype.html`. Stop the preview with Ctrl+C. The walkthrough makes no network requests beyond its own local file. Links to crisis services are documented in the design; the walkthrough's resource actions are inert to avoid accidental calls during demonstrations.

## Planned application organization

The mental-health coursework app will live in its own project folder here: `frontend/` for Vue, `backend/` for FastAPI, `data/skills.db` for its separate SQLite database, and `tests/` for repeatable checks. These are planned paths, not implemented components. This keeps hotel data and all prior assignment behavior separate. Both apps will run only on loopback; the actual future startup commands will be added after implementation.

Reuse candidates are Vue request-state and cancellation patterns, FastAPI validation and credential-safe provider errors, temporary SQLite regression fixtures, and expected-versus-observed documentation. Do not reuse the hotel domain schema, map, generated-SQL execution, booking flow, or the unverified live-LLM claims. Installed Vue/FastAPI/httpx versions were inspected, not copied or newly installed. Exact versions are in [the evidence log](evidence/process.md).

## Later milestones

- **October 22, Part 3.2:** implement one complete paced-breathing skill, model contribution, local session/conversation persistence, measured timing, error/exit behavior, and independent crisis information. STOP is a second-choice extension only if the core experience is verified first.
- **October 29, Part 3.3:** refine history and personalization, run at least 15 fictional scenarios and three cross-case behavior checks, examine limited live-model variation, check clean-checkout instructions, and record the finished demonstration and failure-analysis screencast.

No runtime tests or clinical evaluation are claimed for this design milestone. Proposed schema checks and storyboard navigation checks are narrower experiments. See [verification.md](verification.md).
