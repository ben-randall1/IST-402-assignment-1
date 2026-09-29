# Assignment 2.1 handoff — September 29, 2026

Part 1 extends a copy of the Codex Assignment 1 application in this folder. Original Assignment 1 files are unchanged. Root `.env` and an SQLite backup were copied locally and remain ignored; no credential values are recorded in evidence. System Python has the needed backend packages; the old project's `.venv` is missing httpx and should not be reused as-is.

Implemented live Geoapify hotel discovery, strict U.S. ZIP matching, bounded 5 km/100-record search, independent external-place model, Leaflet map/list synchronization, keyboard selection, all required search states, responsive interface, and preserved sample booking view. Leaflet 1.9.4 was the only newly requested dependency and was approved by the student.

Verification: 20 backend tests, 7 frontend tests, production build, live 16802 (21 hotels), live 02108 (100 hotels/cap notice), list-to-map and keyboard map-to-list selection, invalid/unresolved ZIPs, mobile width check, and original Harbor sample search. Browser checks found and corrected Leaflet initial-view and keyboard-selection defects. Tests and details are in docs/verification.md and docs/evidence/.

Local services: FastAPI at 127.0.0.1:8000 and Vue at 127.0.0.1:5173. See README for startup. Assignment 2 work is on codex/assignment-2-part-1, based on Assignment 1 HEAD ecee2db365bbab080aee4338d4722eb36faab926.

Remaining before Canvas submission: student must record the demo, add the accessible video URL to report.md, and verify instructor access to the private repository. docs/demo-script.md provides the recording outline. Nothing has been submitted to Canvas. Part 2 shortlist is future work.
