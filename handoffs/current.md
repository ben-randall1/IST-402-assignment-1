# Current handoff

## What works

StayScout has a Vue city-search form and a FastAPI endpoint that joins the instructor-supplied `data/hotels.csv` and `data/trips.csv` through `hotel_id`. Matching stays appear in a labeled HTML table with derived nights and price, and zero matches produce a clear message.

The original reviewed checkpoint was `eeb2410dd1176dbd1bee262d6b89001f4826670e`; an updated Part 1 checkpoint with the instructor data is being recorded next.

## Checked

The instructor-data backend check confirms Boston returns `T001`, `T002`, `T009`, and `T010` (four rows) and Miami returns zero rows. `npm run build` completed successfully. In the browser, Boston showed all four rows with calculated prices, and Miami showed the no-results message with no table.

## Limitations and next task

Part 1 uses the instructor CSV pack and a local development API URL. Next task: connect the repository to GitHub, push the Part 1 checkpoint, add instructor-accessible screenshots, then implement Part 2 requirements when assigned.
