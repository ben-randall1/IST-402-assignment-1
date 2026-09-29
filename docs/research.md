# Assignment 2.1 research — September 29, 2026

Prepared before this session's implementation. Sources were read through official product help and developer documentation; these notes do not claim a hands-on competitor usability study.

| Source | Useful pattern / limitation | Decision for StayScout |
| --- | --- | --- |
| [Google Hotels help](https://support.google.com/travel/answer/6276008?hl=en) | A list and map describe the same results. Booking, price, and rating filters depend on additional provider data. | Keep both views connected through one selected place ID. Show only location data supported by Geoapify. |
| [Airbnb search ranking help](https://www.airbnb.com/help/article/39) | Geographic context helps exploration; the documented map and list can differ. That discrepancy would obscure this assignment's selection requirement. | Use exactly the same returned hotels for the map and list, with matching numbers. Panning will not issue a different search. |
| [Geoapify forward geocoding](https://apidocs.geoapify.com/docs/geocoding/forward-geocoding/) | Supports structured postcode lookup, postcode type, and country filtering. A response can omit fields. | Preserve ZIP as text; require the exact requested postcode and U.S. country, valid coordinates, and postcode result type when provided. Reject mismatches instead of accepting a fallback city. |
| [Geoapify Places](https://apidocs.geoapify.com/docs/places/) | Supports hotel category, circle filter in meters, proximity ordering, and bounded pages. Places are not inventory of bookable rooms. | Request `accommodation.hotel` within 5,000 m of the returned point, at most 100 records. Display missing-name/address labels. Label the result cap and coverage limitation. |
| [Leaflet reference](https://leafletjs.com/reference.html) | Markers, events, bounds, and keyboard interaction support linked exploration. Raw HTML in a popup would be inappropriate for provider strings. | Use keyboard-enabled numbered markers and Vue-escaped text; build popup text with DOM `textContent`. Fit the search radius and synchronize selection. |
| [OSM tile policy](https://operations.osmfoundation.org/policies/tiles/) | Public tiles require visible attribution and normal browser caching; no offline prefetching. | Use HTTPS OSM tiles without a credential, keep attribution visible, and show a map-imagery warning if tiles fail. |
| [Geoapify pricing](https://www.geoapify.com/pricing/) | Free tier advertises 3,000 credits/day and up to 5 requests/second at observation time. Costs vary by API use. | Search only on explicit submission; no requests on keystrokes or map movements. Simulate quota failures in tests, never exhaust the live allowance. |

## Early design

See [the early mockup](early-mockup.svg), prepared before implementation in this session. The design uses an editorial cream/forest palette, a prominent ZIP form, a numbered result list, and a map alongside it. Mobile stacks the map and list. A visible status area distinguishes initial, loading, successful results, invalid ZIP, unresolved ZIP, successful empty results, and failed service states. A separate sample-data view preserves Assignment 1 behavior without implying that live hotels have rates or available rooms.

## Starting point

The source was the Codex **Assignment 1** project at `IST 402_ Vibe Coding`, copied including its uncommitted in-class ZIP extension. Original HEAD: `ecee2db365bbab080aee4338d4722eb36faab926`. Existing source stays untouched. Its `.venv` lacks httpx, while system Python 3.11 already imports fastapi, uvicorn, httpx, and dotenv successfully. Existing Vue/Vite packages were copied locally. Leaflet is the only proposed new package; installation requires student approval.
