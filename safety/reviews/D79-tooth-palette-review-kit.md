# D79 review kit: tooth display and severity palette

Prepared for the Clinical Safety Officer (human reviewer). Task S8-T71. This kit **does not contain any approval**; every decision cell is empty on purpose. Nothing here changes code or the hazard log.
Spec reference: `docs/ux/specs/viewer-states.md`. Hazards: HZ-003 (read as a medical conclusion), HZ-009 (severity colour misread or alarming), HZ-011 (patient-reported shown like a clinical finding), HZ-001/HZ-002 (wrong side / region). Rules: BR-020, BR-040, BR-042.

## 1. What is under review
1. Tooth state visuals in the odontogram (caries, filled, missing, implant).
2. Whether caries may use the `severity.moderate` token (orange).
3. Palette names versus their meaning (monitor / mild / moderate / severe / spread / reference).
4. VI and EN wording of each tooth state, the severity labels and the `dental.note` line.

## 2. Evidence: how the screens work today
Source: `apps/web/src/features/viewer/units/dental/Odontogram.tsx`, tokens in `packages/design-system/tokens.json`. The odontogram is a component only: no route reaches it yet.

| Tooth state | Token used | Fill | Non-colour cue | VI label | EN label |
| --- | --- | --- | --- | --- | --- |
| caries | severity.moderate | #D35400 light / #F39C12 dark, 0.75 opacity | solid outline | Ghi nhận sâu răng | Caries noted |
| filled | severity.reference | #8C959F light / #6E7681 dark | dotted outline | Đã trám | Filled |
| missing | (none) | no fill | dashed outline + cross | Mất răng | Missing |
| implant | severity.monitor | #2E7D32 light / #66BB6A dark | ring around tooth | Cấy ghép implant | Implant |

Surfaces (mesial, distal, occlusal, buccal, lingual) are filled only when the record names them; otherwise the whole tooth is filled. Screen-reader text: "Tooth 36: Caries noted, surfaces occlusal".

Palette (all text labels shown beside the colour, BR-020):

| Token name | VI | EN | Light / dark | Contrast on surface (light / dark) |
| --- | --- | --- | --- | --- |
| monitor | Theo dõi | Monitor | #2E7D32 / #66BB6A | 5.1 / 7.8 |
| mild | Nhẹ | Mild | #B7950B / #F4D03F | 2.9 / 12.3 |
| moderate | Trung bình | Moderate | #D35400 / #F39C12 | 4.2 / 8.4 |
| severe | Nặng | Severe | #C0392B / #E74C3C | 5.4 / 4.9 |
| spread | Di căn / lan rộng | Metastasis / spread | #7D3C98 / #BB8FCE | 7.1 / 7.0 |
| reference | Tham khảo | Reference | #8C959F / #6E7681 | 3.0 / 4.0 |

Notes line shown under the chart (`dental.note`):
- VI: "Sơ đồ minh họa những gì được ghi trong hồ sơ của bạn để bạn dễ hiểu hơn, không phải lời khuyên y tế."
- EN: "This chart illustrates what was noted in your record to help you understand it. It is not medical advice."

Other body-map notes (`viewer.note`, `viewer3d.note`) say colours show what was noted in the record.

## 3. Questions for the CSO
Q1. Caries uses the `moderate` token. The record usually states no severity for caries. Does orange tell the reader "moderate" when nothing in the record says so? Options: keep; use a neutral hue for all tooth states; use a dedicated tooth-state palette outside the severity scale.
Q2. Implant is green (`monitor`). Does green suggest "fine" or "being watched" for a device? Filled and missing are grey (`reference`). Is grey right for "missing"? (missing is drawn without fill, grey applies to filled only.)
Q3. Palette names versus meaning: is "Moderate / Trung bình" or "Mild / Nhẹ" appropriate as labels the app shows when the record gave a severity, and what should show when the record gives none (today: Reference / Tham khảo)?
Q4. "Caries noted / Ghi nhận sâu răng": acceptable wording, or must it say "mentioned in your record"? Same for "Missing / Mất răng" (could be read as a diagnosis of loss versus "recorded as missing").
Q5. Is the `dental.note` line enough, or should a state-specific line be shown next to caries?
Q6. `mild` light hex is 2.9:1 on white. Accept with the text label, or require a darker hex?
Q7. Patient-reported tooth entries (BR-040): confirm neutral styling plus "you described / bạn mô tả", no tooth colour from the palette.
Q8. Metastasis style (BR-049 draft): confirm purple `spread` without animation plus the text "stated in your record" is neutral enough.

## 4. Wording to judge (VI / EN)
| Item | VI | EN | Key | Existing or proposed |
| --- | --- | --- | --- | --- |
| Tooth item | Răng 36: Ghi nhận sâu răng, mặt nhai | Tooth 36: Caries noted, surfaces occlusal | dental.item / itemSurfaces | existing |
| Filled | Đã trám | Filled | dental.state.filled | existing |
| Missing | Mất răng | Missing | dental.state.missing | existing |
| Implant | Cấy ghép implant | Implant | dental.state.implant | existing |
| Empty list | Không có răng nào được ghi nhận trong hồ sơ của bạn. | No teeth with notes in your record. | dental.empty | existing |
| Chart note | see section 2 | see section 2 | dental.note | existing |
| Severity labels | see section 2 | see section 2 | viewer.severity.* | existing |
| Patient described | bạn mô tả | you described | viewer.patientReported | proposed |
| Stated in record | được ghi trong hồ sơ của bạn | stated in your record | viewer.statedInRecord | proposed |
| Reference layer | Thông tin tham khảo, không phải tình trạng của bạn | Reference information, not your condition | onco.spreadLayer | proposed |
| Not on chart | Không có trên sơ đồ này | Not shown on this chart | dental.notOnChart | proposed |

## 5. How to produce screenshots (not available in this environment)
Screenshots are not attached because no browser session exists here. The reviewer (or an engineer on request) captures them locally:
1. `pnpm install` then `pnpm --filter @medilens/web dev`; open `http://localhost:3000/vi/...` and `/en/...`.
2. Body map and 3D: `/{locale}/profiles/<profile-id>/body` (needs a profile with confirmed synthetic findings, via the local stack `make up`, synthetic data only).
3. Timeline: `/{locale}/profiles/<profile-id>/timeline` (two or more visits).
4. Odontogram: no route yet. Render it in a throwaway local page (not committed) with synthetic teeth, one of each state, for example `[{fdi:'36',state:'caries',surfaces:['O']},{fdi:'16',state:'filled'},{fdi:'46',state:'missing'},{fdi:'11',state:'implant'}]`, or ask the frontend engineer for a Storybook story.
5. Toggle the dark theme (`data-theme="dark"` on `<html>`) and capture both themes. Capture a colour-blind simulation (browser DevTools, Rendering, Emulate vision deficiencies: protanopia, deuteranopia, achromatopsia) and the 2D fallback (DevTools: block WebGL, or enable Save-Data).
6. Save images under a private location; do not commit images with real data.

| # | Screenshot | VI | EN | Light | Dark | Colour-blind | File / link |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S1 | Odontogram, one tooth per state | [placeholder] | [placeholder] | [placeholder] | [placeholder] | [placeholder] | |
| S2 | Odontogram, caries on several surfaces, selected | [placeholder] | [placeholder] | [placeholder] | [placeholder] | [placeholder] | |
| S3 | Body map with all six severity levels | [placeholder] | [placeholder] | [placeholder] | [placeholder] | [placeholder] | |
| S4 | 3D viewer and 2D fallback with reason | [placeholder] | [placeholder] | [placeholder] | [placeholder] | n/a | |
| S5 | Timeline compare | [placeholder] | [placeholder] | [placeholder] | [placeholder] | n/a | |

## 6. Decision table (CSO to complete; empty by design)
| # | Question | Option A | Option B | Hazard link | CSO decision | Rationale | Date | Initials |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | Caries colour | keep `moderate` | neutral tooth-state palette | HZ-009 | | | | |
| Q2 | Implant and filled colours | keep green / grey | neutral | HZ-009 | | | | |
| Q3 | Palette names vs meaning, fallback label when no severity | keep | change labels | HZ-009, HZ-003 | | | | |
| Q4 | Wording "Caries noted", "Missing" | keep | "mentioned in your record" variants | HZ-003 | | | | |
| Q5 | Extra state-specific note for caries | no | yes | HZ-003 | | | | |
| Q6 | `mild` contrast 2.9:1 | accept with label | darker hex | HZ-009 | | | | |
| Q7 | patient_reported styling | as specced | change | HZ-011 | | | | |
| Q8 | Metastasis neutral style | as specced | change | HZ-007, HZ-009 | | | | |

Outcome: [not decided]. Follow-ups after decisions (not done here): update tokens/labels via PR, hazard-log notes, re-run claims lint, CSO sign-off recorded in the clinical safety case.
