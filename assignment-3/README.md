# A little space · Assignment 3

**Part 3.2 working prototype · October 22, 2026.** Vue, FastAPI and a separate SQLite database, for fictional coursework scenarios on localhost only. This is not therapy, diagnosis, monitored support, or a service for someone in distress. The hotel application remains separately runnable from the repository-root README.

## Run on the checked workspace

No dependencies were installed for Part 3.2. This folder deliberately reuses the already installed Vue/Vite packages in `../frontend/node_modules` through the Vite configuration. Do not run `npm install` in this folder.

From the repository root, in two terminals:

```sh
python3 -m uvicorn main:app --app-dir assignment-3/backend --host 127.0.0.1 --port 8001 --no-access-log
```

```sh
npm run dev --prefix assignment-3/frontend
```

Open `http://127.0.0.1:5174/`. Stop each process with Ctrl+C. Do not use `--host 0.0.0.0`, expose a tunnel, or deploy this prototype. The API has no accounts or multi-user isolation; session UUIDs are record identifiers, not authentication. CORS permits only the local frontend origins.

The backend creates ignored `assignment-3/data/skills.db`. It never opens hotel data. Optional conversation, session checkpoints and an explicitly chosen usual skill are saved there. Local history shows the latest 50 sessions and retrieves transcripts only when you open a session. Deleting a session cascades to its messages, attempts and any usual preference derived from it. The database is unencrypted; enter fictional text only.

### Model configuration

Fill these values in the **ignored repository-root `.env`**, preserving existing settings:

```dotenv
OPENROUTER_API_KEY=your_actual_key
OPENROUTER_MODEL=nvidia/nemotron-3.5-lightning:free
```

The model ID above was verified with two successful production-interface turns and zero reported diagnostic cost. The earlier catalog-listed 3 Super endpoint returned 404 and was explicitly replaced; there is no automatic model switching. Optional reasoning is disabled for the short ID selection, with a 512-token maximum. The model appeared with zero input/output pricing in OpenRouter's public catalog on October 22; free model availability and capacity can change. Use the currently available class-approved free NVIDIA Nemotron ID. Paid IDs are rejected, no alternative paid model is selected, and each explicit Send makes at most one request. Credentials and raw provider errors never reach Vue. Optional messages use OpenRouter; normal operation does not silently substitute fixtures. Missing configuration and failed requests leave the fixed practice and bundled support information available. A server process caps live calls at 50; this is a review-session guard, not an account-wide quota. Restarting the server begins a new counter, so reviewers must track their entire peer session and stop live testing at 50.

The model selects one reviewed orientation response ID using the fictional message, up to four current-session messages, immutable skill content, and an explicitly saved usual choice. It cannot change skill steps, start a timer, write SQL, or generate therapeutic instructions. It is optional before practice and is never awaited during the exercise.

### Explicit fixture demonstration

Stop the normal API first. Run:

```sh
python3 assignment-3/backend/fixture_server.py
```

Keep the same frontend, then reload it. Its banner reads **MOCK MODEL MODE**. The server uses a new temporary database, prints its location, makes no external model calls, and removes that database when stopped. Do not enter real information. Ordinary mock orientation is labeled `[MOCK RESPONSE]`. Fictional messages containing `mock timeout`, `mock rate limit`, `mock malformed`, or `mock network` produce labeled deterministic failures. They do not spend real quota. The normal server never imports this fixture mode.

## Review the experience

1. Choose paced breathing. Optionally ask a fictional question such as “What do the four and six counts mean?”; no message is needed to start.
2. Start six 4-second inhale / 6-second exhale rounds. The visual cue carries the pace; the still-cue toggle and phase words remain usable without animation.
3. Pause, open support, hide the tab, or stop whenever you choose. Closing support never resumes. Resume repeats the interrupted round and records replay/paused time separately. A reload never auto-starts; the previous saved session is marked interrupted when available.
4. On completion, inspect measured time and explicitly save the skill as usual if desired. It is offered on the next entry and never automatically selected or started.
5. Open local history to inspect the transcript and checkpoint. Model failures have no invented successful answer. Local deletion does not delete records held by a provider.

The shared Crisis support panel is bundled in Vue and opens without an API/model/classifier request. Contact links require deliberate activation and depend on the device/connection. **Do not activate contact links during a demonstration.** A conservative substring rule can also open the same panel for an explicit fictional crisis phrase. It can falsely match negation/quotation and miss euphemisms; absence of a match does not establish safety. Nothing is monitored or dispatched.

## Verify

```sh
python3 -m unittest discover -s assignment-3/backend -p 'test_*.py' -v
npm test --prefix assignment-3/frontend
npm run build --prefix assignment-3/frontend
```

All automated model calls are mocks and all databases are temporary. The timer tests inject a monotonic clock and do not replace the separate actual browser duration measurement. See [Part 3.2 evidence](evidence/part-3-2/README.md), [implementation notes](implementation.md), [AI disclosure](../AI-USE.md), and the submitted [report](../report.md).

## Environment and clean checkout

Checked versions: Node 22.19.0, Vue 3.5.42, Vite 7.3.6, plugin-vue 6.0.8; Python 3.11.5, FastAPI 0.116.1, uvicorn 0.35.0, httpx 0.28.1, pydantic 2.13.5, python-dotenv 1.1.1. This milestone verifies the existing workspace, not a clean machine. A reviewer needs the root frontend's lockfile dependencies plus the Python packages in the root backend requirements. Dependency setup is inherited from the earlier project, not duplicated. Inspect local requirements and obtain approval before any installation under AGENTS.md. A clean-checkout run and broader scenario evaluation remain Part 3.3 work.

## Preserve the design milestone

[Part 3.1 report](report-3.1.md), [design rationale](design.md), [research](research.md), [technical plan](technical-design.md), [annotated storyboard](storyboard.svg), [static walkthrough](prototype.html), and [evaluation plan](verification.md) remain historical design artifacts. Their proposed/expected behavior is not evidence that the working version passed a check. The static walkthrough has inert contacts, no model and no real timer; use port 5174 for the implemented app. Part 3.3 adds the full 15-scenario evaluation, live variation, clean-checkout verification and recordings.
