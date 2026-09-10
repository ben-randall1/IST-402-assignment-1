# StayScout — Part 1

## Repository and commit

GitHub repository URL: not configured yet. Exact Part 1 implementation commit: pending the instructor-data checkpoint.

## Implementation

StayScout lets a traveler enter a city and select Search. Vue sends the city to FastAPI and renders matching hotel stays in a plain, labeled HTML table. FastAPI reads the instructor-provided `data/hotels.csv` and `data/trips.csv`, joins trips to hotels using `hotel_id`, filters by city, and derives nights and stay price from hotel rate and trip dates. Backend CSV and join logic remains in Python; Vue owns user interaction and presentation.

## Verification

I manually reviewed the Vue search flow, table labels, FastAPI endpoint, and `hotel_id` join in VS Code/source files. I also built the Vue app with `npm run build` successfully and checked both required scenarios in a browser with the instructor data.

| Action | Expected result | Observed result |
| --- | --- | --- |
| Search `Boston` | Four matching stays display in the table with column labels. | Four rows displayed: `T001`, `T002`, `T009`, and `T010`. Labels shown: Hotel, City, Trip, Check-in, Check-out, Nights, Nightly rate, and Stay price. Calculated stay prices were $300.00, $360.00, $300.00, and $360.00. |
| Search `Miami` | A clear no-results message displays and no table rows appear. | “No hotel stays match ‘Miami’. Try another city.” displayed and the results table was absent. |

## Project context and next steps

Project documentation: [README](README.md), [AGENTS.md](AGENTS.md), [design note](docs/design-note.md), [selected prompts](prompts/selected-prompts.md), and [current handoff](handoffs/current.md).

Remaining limitation: the repository has no GitHub remote configured, so its URL and accessible screenshot links cannot yet be included. Next task: add the remote and push, add instructor-accessible screenshots, then complete Part 2 when its requirements are available.
