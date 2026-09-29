# Part 1 verification record

Date: September 29, 2026 (America/New_York). Live data is time-sensitive; counts below are observations, not assertions about future searches.

## Automated checks

| Input / action | Expected | Observed |
| --- | --- | --- |
| `python3 -m unittest discover -s backend -t . -v` | All postcode, hotel controller, HTTP and sample-data regression checks pass without network calls | 20 tests passed. [Output](evidence/backend-tests.txt). |
| `npm --prefix frontend test` | Request state, validation, errors and stale-response checks pass without API calls | 7 tests passed. [Output](evidence/frontend-tests.txt). |
| `npm --prefix frontend run build` | Vue compiles into production assets | Passed. [Output](evidence/production-build.txt). |
| `.env` ignored and absent from tracked files | `git check-ignore .env` identifies the ignore rule; `git ls-files .env` prints nothing | Passed before commit. Credential-value scan passed for source, documentation, evidence and built frontend. |

Backend coverage includes exact requested postcode, U.S. country, postcode result type when supplied, finite/in-range coordinates, leading zeros, five ASCII digits, 5,000 m request filter, hotel category, 100-result cap, missing names/addresses, geometry fallback, provider-ID deduplication, omitted unusable records, empty success, wholly malformed failure, timeouts, 401/403/429/500 responses at both geocoding and Places stages, and sanitized errors. Legacy checks seed an isolated SQLite database, search Harbor, create a booking, cancel it, reopen the app/database, observe persisted cancellation, then delete it.

Frontend coverage distinguishes loading, invalid, unresolved, successful empty and failed searches; checks preserved leading zeros, selected ID lookup, clearing previous results, network/payload failures and rejection of late responses after a newer search or cancellation. These are composable/state tests, not a substitute for the following browser checks.

## Browser and live checks

| Input / action | Expected | Observed |
| --- | --- | --- |
| Open local preview, submit `16802` | Visible loading then verified postcode point, hotels and map | Loading was visible; State College / 16802 returned 21 hotels. The [dated normalized API snapshot](evidence/live-16802-2026-09-29.json) records center, names, addresses, coordinates, distances and observation timestamp. |
| Click Nittany Lion Inn in the list | Same hotel highlighted on map with popup | Both controls became selected; status showed Nittany Lion Inn at `40.79695, -77.87054`. |
| Submit Boston shortcut `02108` | Leading zero retained; real postcode verified | Boston / 02108 remained intact, with 100 hotels and a visible result-limit notice. First hotel lacked a name; the UI showed “Hotel name unavailable” and its supplied address. |
| Press Enter on map hotel 2 in Boston | Card, marker and status identify the same hotel | After the keyboard correction, both selected Beacon Hill Hotel and Bistro; status showed `42.35691, -71.06965`. |
| Press Space on map hotel 3 in Boston | Same selection behavior as Enter | Both selected Churchill at Boston View. |
| Resize to 390 × 844 | Phone layout stacks map and list; no page overflow | Document width and viewport were both 390 px; map panel was 348 px. Map attribution and list were visible. Viewport restored afterward. |
| Enter `1234` after successful results | Invalid message; no stale hotels/map | Five-digit validation shown; zero hotel cards and zero live maps remained. |
| Enter `00000` | Unresolved ZIP distinguished from successful empty results | “We couldn’t locate that ZIP” and “No verified U.S. location was found for ZIP code 00000.” No hotel cards shown. |
| Open Sample stays and search `Harbor` | Original course data still works | Two sample stays returned, with the course data's $300 two-night prices; clear simulation label remained visible. |

## Failed/revised approaches

1. **Copied dependency executables:** the first build failed because a local folder copy flattened `.bin` symlinks. Restoring the five original package symlinks fixed the build; no new build tool was installed.
2. **Map initialization:** the first live browser run showed hotel cards but an empty map. Console evidence identified a marker element accessed before the map had a view. Initializing Leaflet with the returned center before creating marker DOM fixed it.
3. **Keyboard selection:** Leaflet's default Enter action opened a popup without updating Vue's selected ID. Explicit Enter/Space handling now emits the shared selection event. Repeated browser checks confirmed both directions.
4. **Dense map readability:** Boston reached the cap and many markers overlapped at the full-radius zoom. Selecting a hotel now zooms into its neighborhood; “Show search area” restores the 5 km overview. Coincident provider points can still overlap; all hotels remain reachable from the list and keyboard.

## Remaining limitations

- A screen-recorded demo and instructor-accessible video link are still required; the [recording outline](demo-script.md) is not a substitute.
- The repository is private. Instructor access must be confirmed by the student; no access settings were changed.
- Live results depend on Geoapify coverage, quota and current data. At most 100 provider records are requested. Out-of-radius or invalid records may be omitted with a visible count.
- Empty, failed and quota cases were verified with repeatable automated simulations; live quota was never exhausted. Map tile failure feedback was implemented but no intentional live tile-service outage was induced.
- The persistent external-hotel shortlist is Part 2 work and is not claimed here.
