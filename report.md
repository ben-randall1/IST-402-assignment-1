# StayScout — Part 1

## Repository and commit

GitHub repository URL: not configured yet. Exact Part 1 implementation commit: `eeb2410dd1176dbd1bee262d6b89001f4826670e` (`feat: add Part 1 hotel stay search`).

## Implementation

StayScout lets a traveler enter a city and select Search. Vue sends the city to FastAPI and renders matching hotel stays in a plain, labeled HTML table. FastAPI reads `data/hotels.csv` and `data/trips.csv`, joins trips to hotels using `hotel_id`, filters by city, and returns the matching stay records. Backend CSV and join logic remains in Python; Vue owns user interaction and presentation.

## Verification

I manually reviewed the Vue search flow, table labels, FastAPI endpoint, and `hotel_id` join in VS Code/source files. I also built the Vue app with `npm run build` successfully and checked both required scenarios in a browser.

| Action | Expected result | Observed result |
| --- | --- | --- |
| Search `Boston` | Three matching stays display in the table with column labels. | Three stays displayed: two Harbor House dates and one Beacon Inn date. Labels shown: Hotel, City, Country, Check-in, Check-out, and Price / night. |
| Search `Orlando` | A clear no-results message displays and no table rows appear. | “No hotel stays match ‘Orlando’. Try another city.” displayed and the results table was absent. |

## Project context and next steps

Project documentation: [README](README.md), [AGENTS.md](AGENTS.md), [design note](docs/design-note.md), [selected prompts](prompts/selected-prompts.md), and [current handoff](handoffs/current.md).

Remaining limitation: the repository currently uses concise demo data pending the instructor data pack and has no GitHub remote configured. Next task: replace the CSVs if necessary, add instructor-accessible screenshots after publishing the repository, then complete Part 2 when its requirements are available.
