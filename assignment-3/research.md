# Research notes · October 15, 2026

## Primary source and interpretation

The [Assignment 3 overview](https://psu.instructure.com/courses/2484533/pages/assignment-3-overview-mental-health-skills-application), read in the signed-in browser on October 15, is the supplied research source. It summarizes an ongoing study with 15 patients, 13 clinicians, 15 prototype sessions, and 150 participant–task combinations. It supplies four requirements and six principles; no participant dataset was downloaded or needed. Mention counts describe coded feedback, not clinical effectiveness or independent samples. No clinical outcomes are inferred.

The design uses the instructor's exact 4–6 breathing structure. Other sources inform interface and engineering choices, not alternate therapeutic instructions. All scenario text is invented for coursework.

| Code | Finding in the assignment (paraphrased) | Implication adopted here |
| --- | --- | --- |
| R1 | Participants disengaged beyond roughly 90–100 seconds; around a minute was comfortable. | Six ten-second cycles; measure actual first-instruction-to-last-step time. |
| R2 | Crisis information must be reachable without a screen journey. | A persistently labeled control opens embedded information directly. |
| R3 | Stopping must carry no penalty. | Stop exits immediately; no reason, completion score or guilt message. |
| R4 | People want control over the path they take. | Explicit start/change/leave; a recommendation never starts a skill. |
| D1 | More distress suggests less interface, but the study provides no reliable detector. | A user-selected “Less on screen” mode; no distress inference. |
| D2 | One action per exercise screen was preferred. | Show only the current inhale/exhale cue, plus persistent safety/exit controls. |
| D3 | Disclosure and performance can carry emotional cost. | No mandatory mood rating, reason, typing or post-exercise report. |
| D4 | Safety must remain visible inside exercises. | Keep the resource control outside the changing skill component. |
| D5 | Personalization should avoid settings work. | Optional one-tap “Use this as my usual”; show its origin and keep alternatives. |
| D6 | Clinical, overly cheerful language and demanding stimulation were unwelcome. | Plain invitations, quiet colors, no congratulatory scores, optional motion. |

The complete tradeoffs and checks are in [design.md](design.md). These decisions are our interpretation of the class findings, not findings independently demonstrated by this project.

## Existing interfaces and implementation references

| Source reviewed | Useful observation | Limitation / adopted decision |
| --- | --- | --- |
| [Headspace breathing-exercise article](https://www.headspace.com/meditation/breathing-exercises) | Describes a short guided breathing example and visual pacing. | The public page also contains extensive reading and promotional choices. Use a concise cue and separate context from the active exercise. The class's 4–6 sequence stays fixed. No logged-in app evaluation or efficacy comparison was performed. |
| [VA PTSD Coach product documentation](https://mobile.va.gov/app/ptsd-coach) and [official interface overview](https://www.ptsd.va.gov/appvid/mobile/ptsdcoach_app.asp) | Separates coping tools and access to support. | Its clinical population and broader feature set do not make it a template for our entire experience. Keep support visible during a skill instead of relying on a home-screen category. This is a review of published product information, not hands-on testing or endorsement. |
| [W3C: Animation from Interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) | Motion can be distracting and users need control. | Supply a static phase label/countdown when reduced motion is preferred. Removing animation must not remove pacing information. This reference does not certify accessibility compliance. |
| [MDN: performance.now](https://developer.mozilla.org/en-US/docs/Web/API/Performance/now) | Provides a monotonic elapsed-time basis. | Future timer should compute from elapsed time rather than assume every callback fires on time. Backgrounding pauses the skill and requires explicit resume. A timing design is not a measured runtime result. |

Resource lookup: the connected helpline tool returned U.S. crisis contact details on October 15. The planned support panel uses only those returned contact routes, explicitly labels the U.S. region, and does not assume a number works globally. [Safety copy and links](technical-design.md#independent-crisis-support). No service was called or messaged during research.

The first attempted legacy VA documentation URL was unavailable in the web tool. The final research uses the current official VA Mobile listing and National Center for PTSD interface overview instead. No inaccessible page is cited as inspected.

## Scope and omitted data

The optional Kaggle conversation dataset was not used. The class already supplies the skill steps and design evidence; importing therapy-like conversation data would add provenance and review work without answering the current design questions. We did not register with or converse with Character.AI or another support service. The application will not infer diagnoses, choose a skill from a clinical score, or train on user conversations.
