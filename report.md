# Assignment 2.1 — Live Hotel Search and Map

**Student:** Ben Randall
**Course:** IST 402, Section 003
**Observation date:** September 29, 2026
**Project:** StayScout

> **Submission status:** Implementation and local verification are complete. Before submitting, publish this local Assignment 2 branch with student approval, add the required screen-recorded demo link below, and confirm that the instructor can open the private repository and linked artifacts. The branch/artifact URLs below are prepared for publication and are not yet available remotely. This report has not been submitted to Canvas.

## 1. Project access and startup

- Repository / Assignment 2 branch: [StayScout — codex/assignment-2-part-1](https://github.com/ben-randall1/IST-402-assignment-1/tree/codex/assignment-2-part-1).
- Assessed implementation commit: **6bd37a28a8785411555e70231a3716f8da7e2843**. The report's final commit can follow this code checkpoint.
- Startup and configuration: [README](https://github.com/ben-randall1/IST-402-assignment-1/blob/codex/assignment-2-part-1/README.md).
- MVC and verification guidance: [AGENTS.md](https://github.com/ben-randall1/IST-402-assignment-1/blob/codex/assignment-2-part-1/AGENTS.md).

Start FastAPI from the project root with `python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`, then run `npm --prefix frontend run dev`. Open `http://127.0.0.1:5173/`. A fresh checkout requires the declared Python/frontend dependencies and a Geoapify key in the ignored root `.env`; follow the README's environment check and installation-approval instructions first. All backend provider requests use that local key. The map uses public OpenStreetMap tiles, so no backend credential is exposed to the browser.

The project extends the existing Vue/FastAPI/SQLite application. Existing hotel/trip joins, sample search, simulated booking CRUD, and SQLite data are preserved in the labeled **Sample stays** view. The Assignment 1 source folder remains unchanged.

## 2. Research notes

Research was conducted before this session's implementation through official product help and developer documentation. [Full notes and source links](https://github.com/ben-randall1/IST-402-assignment-1/blob/codex/assignment-2-part-1/docs/research.md).

- [Google Hotels](https://support.google.com/travel/answer/6276008?hl=en): its connected list/map provides useful spatial context. Price and booking controls rely on data this API does not supply, so StayScout includes only supported location information.
- [Airbnb search help](https://www.airbnb.com/help/article/39): map exploration is useful, but its documented list/map membership can differ. StayScout deliberately uses one returned collection and one selected place ID for both views.
- [Geoapify geocoding](https://apidocs.geoapify.com/docs/geocoding/forward-geocoding/): structured postcode lookup and country filtering support ZIP searches. StayScout also verifies the returned postcode, U.S. country and coordinates rather than trusting a fallback result.
- [Geoapify Places](https://apidocs.geoapify.com/docs/places/): hotel categories, radius filtering and bounded results fit discovery. They do not establish room availability; missing names/addresses receive honest labels.
- [Leaflet](https://leafletjs.com/reference.html) and [OSM tile policy](https://operations.osmfoundation.org/policies/tiles/): keyboard markers, shared events and visible attribution informed the map. Public HTTPS tiles use normal browser caching; there is no offline prefetch feature.
- [Geoapify pricing](https://www.geoapify.com/pricing/): free-tier usage is bounded. Search requires explicit submission; panning and typing do not make provider requests. Tests simulate failures instead of exhausting quota.

## 3. Early mockup and changes

[View the early SVG mockup](https://github.com/ben-randall1/IST-402-assignment-1/blob/codex/assignment-2-part-1/docs/early-mockup.svg). It was saved before implementation and shows the ZIP form, matching numbered hotel cards/map pins, 5 km circle, missing-field treatment and state notes.

The implementation retains the cream/forest visual direction and connected views. An explicitly labeled map illustration was added for the initial state. Phone layouts put the map above the list. “Show search area” restores the radius overview; selecting a hotel zooms into its neighborhood. A disclosure explains the search center, distances and coverage limits. Legacy booking behavior remains in a separate, clearly labeled sample-data view.

## 4. Screen-recorded demonstration

**Video link: PENDING — record the finished application and insert an instructor-accessible URL before submission.**

[Recording outline](https://github.com/ben-randall1/IST-402-assignment-1/blob/codex/assignment-2-part-1/docs/demo-script.md). It covers live ZIP search, list/map selection, keyboard input, leading zeros, invalid/unresolved ZIPs, coverage limitations and preserved sample behavior. The outline is not a substitute for the required video.

## 5. Verification record

[Full expected-versus-observed record](https://github.com/ben-randall1/IST-402-assignment-1/blob/codex/assignment-2-part-1/docs/verification.md), [backend output](https://github.com/ben-randall1/IST-402-assignment-1/blob/codex/assignment-2-part-1/docs/evidence/backend-tests.txt), [frontend output](https://github.com/ben-randall1/IST-402-assignment-1/blob/codex/assignment-2-part-1/docs/evidence/frontend-tests.txt), and [build output](https://github.com/ben-randall1/IST-402-assignment-1/blob/codex/assignment-2-part-1/docs/evidence/production-build.txt).

| Input / action | Expected | Observed on September 29, 2026 |
| --- | --- | --- |
| Live ZIP `16802` | Verify exact U.S. ZIP, find hotels within 5 km, show matching map/list | State College / 16802; 21 returned hotels. [Dated response snapshot](https://github.com/ben-randall1/IST-402-assignment-1/blob/codex/assignment-2-part-1/docs/evidence/live-16802-2026-09-29.json). |
| Select Nittany Lion Inn in list | Same hotel selected on map | Matching selected card/marker and popup; displayed coordinates `40.79695, -77.87054`. |
| Live ZIP `02108` | Preserve leading zero | Boston / 02108; 100 results and a visible cap notice. A missing name received “Hotel name unavailable.” |
| Enter / Space on Boston map pins | Same selected hotel in the list | Enter selected Beacon Hill Hotel and Bistro; Space selected Churchill at Boston View. |
| `1234` after results | Invalid input; obsolete results cleared | Five-digit message, no remaining hotel cards or live map. |
| `00000` | Unresolved postcode, not an empty hotel search | Explicit no-verified-U.S.-ZIP message. |
| 390 × 844 viewport | Responsive map/list without horizontal overflow | Page width equaled viewport width; map and attribution visible. |
| Sample view: `Harbor` | Existing behavior preserved | Two supplied sample stays returned with their original calculated prices. |
| Automated backend / frontend suites | Repeatable edge-case checks | 20 backend tests and 7 frontend tests passed; production build passed. |

Live counts are dated observations, not fixed test assertions. Automated tests simulate successful empty results, wrong-location responses, timeouts, malformed data, quota/rate-limit responses, and missing fields. Service errors cannot become successful empty results. The sample booking regression uses a temporary SQLite database and verifies creation, cancellation, persistence on reopening, and removal.

Corrections during verification: restore package executable symlinks after a local copy; initialize the Leaflet view before accessing marker DOM; explicitly handle Enter/Space so popup selection also updates Vue state. These are documented in the evidence log.

## 6. AI disclosure and evidence

**Tool:** OpenAI Codex desktop. **Model:** GPT-6 Astra (`gpt-6-astra`). Used for assignment review, official-source research, early mockup, implementation, automated checks, browser verification, and report drafting. No subagents or other AI models were used in this session.

[Selected prompt excerpts, code links and revised approaches](https://github.com/ben-randall1/IST-402-assignment-1/blob/codex/assignment-2-part-1/prompts/assignment-2-evidence.md). The student identified the existing Assignment 1 project and explicitly approved adding Leaflet 1.9.4 after an environment check. Existing Vue/Vite and backend packages were reused. Prior Assignment 1 work predates this session and is not attributed to Astra here.

## 7. Limits and remaining submission work

The provider request is capped at 100 records and coverage is not exhaustive. The 5 km radius is centered on the returned postcode point, not the traveler's position or the complete ZIP area. Distances are calculated straight-line estimates. There are no invented hotel prices, ratings, room availability or live booking confirmations. Co-located markers can overlap; each returned hotel remains accessible through its list control.

The Part 2 persistent live-hotel shortlist is not implemented or claimed in this Part 1 submission. Existing SQLite sample bookings are distinct from that future feature.

Before upload: add the real video link, confirm instructor access to the private repository and every artifact, review the report, and submit this `report.md` to the Part 1 Canvas assignment. No deployment or paid plan is required.
