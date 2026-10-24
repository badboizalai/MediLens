# Sprint 09 Report

Sprint dates: 2027-02-17 to 2027-03-02 (plan D81-D90; PRs merged 2026-10-23 to 2026-10-24) | Owner: PO/PM | Status: Draft (review D90 not held)

## Goal
3D body and heart viewer with picking, a performance budget with 2D fallback, the cardiology Unit, compatibility tests and security headers. Met: partly. The viewer and fallback are merged, but the GLB files are procedural placeholders, no usability test has run, and device FPS is not measured.

## Delivered items
| Task | Item | PR | Status |
| --- | --- | --- | --- |
| D81 S9-T81 | 3D body viewer with region picking (covers the spike and D83) | #109 | merged |
| D82 S9-T82 | Body and heart GLB with `region_code` meshes and LOD. Stylised procedural placeholders, not real anatomy, no Draco; real asset (BodyParts3D / Z-Anatomy) pending licence review | #104 | merged (partly) |
| D83 S9-T81 | Raycast picking, highlight, detail panel | #109 | merged |
| D84 S9-T84 | 3D performance budget with automatic 2D fallback (FPS threshold in code, not measured) | #114 | merged |
| D85 S8-T75 | Cardiology Unit config with LOINC subset (delivered in S08) | #100 | merged |
| D86 S8-T76 | Cardiology golden docs (200) inside the 600-doc set; cardiology prompts not evidenced | #118 | merged (partly) |
| D88 S7-T67 | Compat matrix (NFR-17): chromium, firefox, Pixel 7 pass; WebKit and iPhone 14 not run (missing system libraries) | #135 | merged (partly) |
| D89 S9-T89 | CSP, security headers, CORS allow-list | #113 | merged |

## Not delivered / carried over
- D87 usability test with 5 people (task success, SUS): not run, no `ux/usability-r1.md`. Human-only.
- D88: WebKit and iPhone 14 not run; branded Edge and Safari, real iOS 16 and Android 10 devices not covered; the e2e CI job is not wired.
- D82: real open-licence anatomy with 4 chambers, valves and coronaries, and Draco/meshopt.
- D84: FPS on a weak device not measured.
- D86: cardiology extraction prompts (echo, text ECG).
- D90 demo (rotate, zoom, region click): not run.

## Human-only open items
- D87 usability test with 5 people (recruit, run, record).
- D90 sprint review and retro.
- Licence review of the real 3D anatomy source (CC BY-SA attribution) before replacing placeholders.
- Terraform apply for staging.

## Top risks
| ID | Risk | Score | Change | Action |
| --- | --- | --- | --- | --- |
| R10 | Laggy 3D on weak devices | 12 | mitigation added (#114) | Measure FPS on a weak device |
| R09 | Asset licence | 9 | none | Placeholder assets carry no external licence; real asset needs a register row |
| R01 | Illustration read as medical advice | 15 | none | Usability evidence still missing |

## Metrics
| Metric | This sprint | Previous | Target |
| --- | --- | --- | --- |
| Committed vs done (say/do) | 8 of 9 build rows (D81-D89) have a merged PR; D85 and D88 landed under other sprints' ids; 5 complete, 3 partial; D87 human-only | 8 of 9 (S08) | n/a |
| Velocity (rolling 3) | n/a | n/a | n/a |
| Open S1/S2 bugs | n/a (not measured) | n/a | 0 |
| Cloud + LLM cost (USD) | n/a | n/a | n/a |

## Retro
Based on `docs/operations/autopilot-state.md` run 4; human to confirm.
- Keep: stating plainly in the PR that assets are placeholders and thresholds are not measurements.
- Drop: counting a threshold in code as a performance result.
- Try: run the WebKit projects in CI with `playwright install --with-deps`.

| Action | Owner | Due |
| --- | --- | --- |
| Recruit 5 participants for the D87 test | PM | human to set |

## Learned
- Plan row ids and task ids drift (D85 and D88 were delivered under S8-T75 and S7-T67); map rows to PRs explicitly.
