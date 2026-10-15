# Static walkthrough browser review · October 15, 2026

**Target:** `http://127.0.0.1:5184/prototype.html`, served locally with Python's existing standard library. This is the Part 3.1 design storyboard, not the future Vue/FastAPI app. No therapeutic test, real distress input, model call, timer-duration measurement or application persistence check occurred.

| Action / input | Expected | Observed |
| --- | --- | --- |
| Open entry | Clear prototype boundary; breathing choice; no automatic start | Visible coursework/review banner, explicit Choose breathing and separate ready/Start steps. [Entry screenshot](design-entry.png). |
| Choose breathing; activate Start with Enter | One current breathing cue; support and stop available | Inhale static cue “4”; Pause/Stop and shared Crisis support/Leave visible. [Skill sketch](design-skill.png). This is not a running timer. |
| Use reviewer selector across all 12 screens | Each has a main heading and support/leave controls | All 12 passed visible-control checks. [Recorded checks](storyboard-screen-checks.json). |
| Open/close support on each of 12 screens | Static panel opens regardless of simulated model state | All 12 opened correctly. [Recorded checks](storyboard-support-checks.json), [panel screenshot](design-support.png). Contacts are inert. |
| Open support during inhale and press Escape | Return to a paused screen rather than restarting | Paused heading shown, explicit Resume/Stop; focus returned to Crisis support. |
| Less on screen at entry | Remove examples/sidebar without hiding core choice, history, support, leave or reversal | Main choice remained; More on screen and View history visible; sidebar and optional message hidden. |
| Ending → Use this as my usual → Done | Offer the remembered choice without auto-start | Entry showed “Your usual · You chose this” and Use my usual/Clear usual; cleared successfully. This state is page memory only. |
| 390 × 844 simulated model failure | Readable controls and no horizontal overflow; support panel opens | Document width = viewport width = 390; support opened and Escape closed it. [Mobile screenshot](design-mobile.png). Temporary viewport was reset. |
| Open storyboard SVG | Inspectable sketch, legible annotations and intended hierarchy | Six frames rendered with shared support/leave and study-code notes. SVG syntax also checked by script. |

Correction during review preparation: the shared header was made sticky so support/leave remain visible while scrolling a long design screen. This is a storyboard improvement, not proof of a runtime application's safety route. The first artifact-link check caught the browser-review document before it had been created; it was then added and checks rerun.

Not checked: full WCAG compliance, assistive-technology testing, runtime scheduling, persistent session UI, actual network outage handling, live model variation or use by anyone in distress. The proposed tests in verification.md remain planned.
