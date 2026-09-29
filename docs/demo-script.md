# Part 1 screen recording outline

Record the running application after the final checks, then place an instructor-accessible video link in `report.md`. This outline is not a video and is not evidence that recording is complete.

1. Show the StayScout landing page and explain that this is hotel location discovery. Enter ZIP `16802`, submit, and let the loading state finish. Identify the live observation date.
2. Show the verified locality/ZIP, returned hotel count, 5 km radius, and attribution. Explain that the count may change over time and that the center is Geoapify's postcode point.
3. Click a hotel card. Show its highlighted map marker and popup. Select a different map marker with the mouse, then use keyboard Tab/Enter or Space. Show that the corresponding card and selected-hotel text update.
4. Search `02108` to demonstrate a leading-zero ZIP. Do not describe this as your own location.
5. Enter `1234`. Show the invalid-input message and that obsolete results disappear. Search `00000` to show unresolved-ZIP behavior; if the provider changes that response, describe what actually happened.
6. Expand “How search works.” Mention the 100-result limit, variable coverage, straight-line distances, and absent rates/ratings/availability.
7. Briefly show **Sample stays**, clearly identified as supplied course data and simulated bookings; return to live discovery.
8. Show successful automated checks in a terminal if time permits: `python3 -m unittest discover -s backend -t . -v`, and `npm --prefix frontend test`. Explain that empty, network, quota, wrong-location and missing-field cases are simulated without exhausting the service.

Keep the recording focused on the browser and relevant test output. Do not show `.env`, credentials, account settings, or unrelated private tabs. Upload the final recording to a location your instructor can access, then replace the report's pending video field. Review every link before submitting `report.md` to Canvas.
