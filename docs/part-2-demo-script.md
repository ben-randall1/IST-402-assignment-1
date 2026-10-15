# Part 2 recording outline

**A real screen-recorded video is still required. This outline is not a video or proof of a live LLM call.**

1. Configure `OPENROUTER_API_KEY` and the available class `OPENROUTER_MODEL` in ignored `.env` before recording. Do not record the file or key. Use the normal backend, not the fixture runner. State the exact model ID and observation date.
2. Show Explore with ZIP 16802. Save returned hotels; show the simulated date/rate/room rows and local-first subset. Restart both backend/browser to show persistence. Explain duplicate saves do not overwrite edited nights. For removal evidence use an additional saved test hotel; preserve the two used in your live comparison.
3. Open Ask StayScout. Submit “Which saved hotels in ZIP 16802 have a room from October 10 to October 12, 2026, for under $250 total? Compare the total costs.” Show loading and the displayed live answer.
4. Expand the evidence. Show the original question, model-proposed SQL, hotel IDs and nightly rows, returned totals, exact model ID, and answer. Compare expected $200 per default two-night stay with observed results. Explain October 12 is checkout, not a third charged night. State that prices and rooms are simulated, although locations came from Geoapify.
5. Ask about October 20–22, 2026. Show the empty retrieved data and no-match/insufficient-data answer. It is not a claim that the destination has no hotels.
6. Clearly switch to **offline fixture verification**. Show `python3 -m backend.verify_part2` and its JSON: the mocked model proposed `DELETE FROM saved_hotels`; backend returned 422; database bytes were unchanged; answer call was not executed. Show mocked 429 separately. Do not deliberately exhaust live quota.
7. Show fixed fixture expectations: Pine $200 vs Elm $240; missing/sold-out nights excluded; two rooms require $400 at Pine. Link the JSON sample for repeatability.
8. Show preserved list/map selection and Sample stays → Harbor. Close by identifying the scope: local subset, no real bookings, no invented live prices, capped retrieval.

After recording, put an instructor-accessible video URL in `report.md`. Verify the published assessed commit and artifact links using the instructor's intended access. Record a real live trace separately from `part-2-mock-workflow.json`. Do not upload the report while these entries are pending.
