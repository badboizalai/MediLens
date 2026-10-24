# Sprint 08 Report

Sprint dates: 2027-01-27 to 2027-02-16 (plan D71-D80; PRs merged 2026-10-23 to 2026-10-24) | Owner: PO/PM | Status: Draft (review D80 not held)

## Goal
2D viewer, FDI odontogram and the dental Unit. Met: partly. Viewer components, assets, Unit configs and the 600-document golden set are merged; the CSO review of tooth display and palette (D79) and the demo are not done.

## Delivered items
| Task | Item | PR | Status |
| --- | --- | --- | --- |
| D71 S8-T71 | Viewer state spec and D79 tooth/palette review kit (no Figma file evidenced) | #127 | merged (partly) |
| D72 S8-T72 | 2D body SVG front/back with `region_code` ids | #66 | merged |
| D73 S8-T73 | 2D body viewer: severity colours, tooltip, region list | #93 | merged |
| D74 S8-T74/74b | FDI odontogram SVG; viewer with surface states | #95, #105 | merged |
| D75 S8-T75 | Dental and cardiology Unit configs with LOINC subset | #100 | merged |
| D76 S8-T76 | 600-doc synthetic golden set per Unit with stratified eval (dental prompts not evidenced) | #118 | merged (partly) |
| D77 S8-T77 | Dental VI-EN terminology (57 terms); ICD-10 gated on LIC-002 | #91 | merged (partly) |
| D78 S8-T78 | 2D viewer and odontogram snapshot regression | #132 | merged |
| S8-CLIN | Confirmed extraction projected into clinical findings | #112 | merged |
| S8-GAPS | Viewer gaps: side switch, dental route, legend, 3D controls | #138 | merged |

## Not delivered / carried over
- D79 CSO review of tooth display and severity palette: not done (human). Only the review kit exists (#127).
- D77: ICD-10 K00-K14 codes not loaded (LIC-002 open).
- D76: dental prompts and rules not evidenced; the golden set covers data only.
- D80 demo of an odontogram coloured from a record: not run.

## Human-only open items
- D79 CSO review of tooth display and severity palette; dental term wording.
- D80 sprint review and retro.
- LIC-002 ICD-10 and LIC-003 LOINC decisions.
- Terraform apply for staging.

## Top risks
| ID | Risk | Score | Change | Action |
| --- | --- | --- | --- | --- |
| R01 | Illustration read as medical advice | 15 | none | The D79 palette review is the gate |
| R19 | Dataset or code list used outside licence | 12 | none | ICD-10 stays gated; no code loaded |
| R06 | No real data | 15 | golden set now 600 synthetic docs (#118) | Real-data work stays blocked until G3-P |

## Metrics
| Metric | This sprint | Previous | Target |
| --- | --- | --- | --- |
| Committed vs done (say/do) | 8 of 9 build rows (D71-D79) have a merged PR; 5 complete, 3 partial; D79 is human-only | 9 of 9 (S07) | n/a |
| Velocity (rolling 3) | n/a | n/a | n/a |
| Open S1/S2 bugs | n/a (not measured) | n/a | 0 |
| Cloud + LLM cost (USD) | n/a | n/a | n/a |

## Retro
Based on `docs/operations/autopilot-state.md` run 4; human to confirm.
- Keep: asset tests in `testpaths`; snapshot regression for viewers.
- Drop: calling viewer work done before it is mounted on a page (run 4 flagged BodyMap2D mounting and the `?raw` rule in `next build` as open).
- Try: verify `next build` for each new viewer PR.

| Action | Owner | Due |
| --- | --- | --- |
| Book the D79 review with the CSO | PM | human to set |

## Learned
- A review kit (#127) prepares a human review; it is not the review.
