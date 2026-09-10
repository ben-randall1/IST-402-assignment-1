# Current handoff

## What works

StayScout has a Vue city-search form and a FastAPI endpoint that joins the instructor-supplied `data/hotels.csv` and `data/trips.csv` through `hotel_id`. Matching stays appear in a labeled HTML table with derived nights and price, and zero matches produce a clear message.

The submitted Part 1 implementation checkpoint with the instructor data is `8ac03e41e47ddf32e560bcaf664229a7944a656b`.

## Checked

The instructor-data backend check confirms Boston returns `T001`, `T002`, `T009`, and `T010` (four rows) and Miami returns zero rows. `npm run build` completed successfully. In the browser, Boston showed all four rows with calculated prices, and Miami showed the no-results message with no table.

## Limitations and next task

Part 1 uses the instructor CSV pack and a local development API URL. Next task: connect the repository to GitHub, push the Part 1 checkpoint, add instructor-accessible screenshots, then implement Part 2 requirements when assigned.
