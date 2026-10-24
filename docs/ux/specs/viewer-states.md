# Viewer state spec: 2D body map, odontogram, 3D viewer, timeline

Task S8-T71. Owner: medilens-ux-ui-designer. Reviewer: clinical-safety-officer (human, D79). Status: draft v0.1, **not approved**.
Complements `docs/ux/wireframes/viewer.md` (layout) and `docs/ux/wireframes/timeline.md`. This file is the per-state contract plus the list of gaps against code at commit `6ea6508`.
Rules: BR-013, BR-015, BR-020, BR-021, BR-040, BR-042, BR-046 to BR-051 (BR-046..051 are drafts pending CSO). Hazards: HZ-001, HZ-002, HZ-003, HZ-007, HZ-009, HZ-010, HZ-011.
Copy keys: **existing** = present in `apps/web/messages/{en,vi}.json`; **proposed** = does not exist yet. Wording rule: describe what the record says; never "you have"; point meaning to the doctor.

## 1. Shared rules

### 1.1 Severity legend (text label always, BR-020)
Tokens from `packages/design-system/tokens.json`; labels from `viewer.severity.*` (existing). Contrast is measured against `brand.surface` (white in light, `#0F1419` in dark); WCAG 1.4.11 needs 3:1 for graphics.

| Key | VI | EN | Icon (token) | Light hex / ratio | Dark hex / ratio | Non-colour cue in 2D map |
| --- | --- | --- | --- | --- | --- | --- |
| monitor | Theo dõi | Monitor | eye | #2E7D32 / 5.1 | #66BB6A / 7.8 | none beyond text |
| mild | Nhẹ | Mild | circle-small | #B7950B / 2.9 (below 3:1) | #F4D03F / 12.3 | none beyond text |
| moderate | Trung bình | Moderate | circle-half | #D35400 / 4.2 | #F39C12 / 8.4 | none beyond text |
| severe | Nặng | Severe | circle-full | #C0392B / 5.4 | #E74C3C / 4.9 | none beyond text |
| spread | Di căn / lan rộng | Metastasis / spread | arrows-out | #7D3C98 / 7.1 | #BB8FCE / 7.0 | dashed 6 3 outline |
| reference | Tham khảo | Reference | info | #8C959F / 3.0 | #6E7681 / 4.0 | dotted 2 2 outline |

Notes: fill is drawn at 0.75 opacity, so effective contrast is lower than the table; the 2 px `currentColor` outline (textMuted) carries the 3:1 requirement. Four levels differ only by colour inside the map and by text in the list, tooltip and aria-label. That meets BR-020 only because the text label is always adjacent (gap 3).
Legend (proposed): a visible key under every map with swatch + icon + label for the levels present on screen; key `viewer.legend.title` (proposed): VI "Chú giải màu", EN "Colour key".

### 1.2 Source styling
| Source | Styling | Copy |
| --- | --- | --- |
| Confirmed from record | severity swatch + label | `viewer.severity.*` (existing) |
| patient_reported (BR-040) | no severity colour, no ICD code; neutral fill (`brand.surfaceMuted`) + speech-bubble icon + thin solid border; the `reference` hue is not reused; always the text "you described" | `viewer.patientReported` (proposed): VI "bạn mô tả", EN "you described" |
| Metastasis stated in record (BR-021, BR-049 draft) | neutral style: `spread` token is the only colour, no animation, flashing or pulsing; text names the site and says it is stated in the record | `viewer.severity.spread` (existing) + `viewer.statedInRecord` (proposed): VI "được ghi trong hồ sơ của bạn", EN "stated in your record" |
| "Possible spread" educational layer | off by default, always labelled | `onco.spreadLayer` (proposed in messages): VI "Thông tin tham khảo, không phải tình trạng của bạn", EN "Reference information, not your condition" |
| Oncology record, first open (BR-046 draft) | summary mode, no metastasis layer until "Show details" | `viewer.showDetails` (proposed): VI "Xem chi tiết", EN "Show details" |

### 1.3 Persistent notes
Every viewer shows one illustration note (existing: `viewer.note`, `viewer3d.note`, `dental.note`) and the page-level `DisclaimerBar`. No note may use medical-conclusion, medication or outlook language (claims lint covers `docs/ux` and `apps/web/messages`).

### 1.4 State vocabulary
- Empty: nothing confirmed, call to action to upload. Partial: some findings, some unmapped / side unknown / undated. Full: every confirmed finding drawn. Error: data or asset failed. Fallback: 3D unavailable, 2D shown with a reason.
- No state hides the text list; the list is the accessible equivalent of the picture.

## 2. 2D body map (`BodyMap2D`, front/back)

| State | What shows | Copy keys | Keyboard / screen reader |
| --- | --- | --- | --- |
| Loading | Silhouette skeleton + status text | `timeline.loading` (existing, reused by screens); generic `common.loading` (proposed) | `role=status` |
| Empty | Plain outline, list heading, "No regions with findings on this side", note; CTA to upload | `viewer.empty`, `viewer.listTitle`, `viewer.note` (existing); CTA `viewer.emptyCta` (proposed): VI "Tải hồ sơ lên", EN "Upload a record" | figure labelled `viewer.front` / `viewer.back`; no tab stops in the map |
| Partial | Coloured regions + list; unknown region codes are not drawn or listed (callback `onUnknownRegion`); highest severity wins for a repeated region | `viewer.item` = "{region}: {severity}" | each coloured region `tabIndex=0`, `role=img`, `aria-label` = list text; tooltip on hover and focus |
| Full | All mapped findings coloured and listed | same | same |
| Unmapped (HZ-002) | Never placed on the body; listed in an "Unmapped" group | `finding.unmapped` (proposed) | list only |
| Side not stated (HZ-001) | Not drawn on either side; listed with "side not stated" | `viewer.sideUnknown` (proposed): VI "không rõ bên", EN "side not stated" | list only |
| Resected organ (HZ-010) | Ghost outline + label | `viewer.resected` (proposed): VI "đã cắt bỏ (theo hồ sơ)", EN "removed (per your record)" | in list and aria-label |
| Error | ErrorState with Retry; list still attempted | `viewer.error` (proposed): VI "Chưa tải được hình cơ thể. Danh sách bên dưới vẫn dùng được.", EN "We couldn't load the body view. The list below still works." | `role=alert` |

Dark mode: swatches switch to the `dark` hex; outline follows `currentColor`.

## 3. Odontogram (`Odontogram`, FDI, clinician view)

| State | What shows | Copy keys | Keyboard / screen reader |
| --- | --- | --- | --- |
| Empty | 32-tooth outline, no fill; "No teeth with notes in your record" | `dental.empty`, `dental.note` (existing) | teeth `aria-hidden`; chart `role=group` labelled `dental.chartLabel` |
| Partial | Only teeth with a state are interactive; surfaces M/D/O/B/L filled when named, whole tooth when none named; unknown FDI ignored (dev console warning only) | `dental.item`, `dental.itemSurfaces`, `dental.state.*`, `dental.surface.*` | Tab to each affected tooth; Enter/Space toggles selection (`aria-pressed`); selection announced via `role=status` (`dental.details`) |
| Full | As partial; list under the chart repeats every item | `dental.listTitle` | list is the text alternative |
| Error | Chart asset cannot render: list only + error string | `viewer.error` (proposed) | `role=alert` |
| Tooth not on chart (primary teeth, bad FDI) | Listed only, "not shown on this chart" | `dental.notOnChart` (proposed): VI "Không có trên sơ đồ này", EN "Not shown on this chart" | list only |

Tooth state visuals (subject of D79, see `safety/reviews/D79-tooth-palette-review-kit.md`):

| State | Fill token | Non-colour cue | VI | EN |
| --- | --- | --- | --- | --- |
| caries | severity.moderate (orange) | solid outline, 0.75 fill | Ghi nhận sâu răng | Caries noted |
| filled | severity.reference (grey) | dotted outline (1 1) | Đã trám | Filled |
| missing | none (no fill) | dashed outline (3 2) + cross | Mất răng | Missing |
| implant | severity.monitor (green) | ring around the tooth | Cấy ghép implant | Implant |

## 4. 3D viewer (`BodyViewer` + `BodyViewer3D`)

| State | What shows | Copy keys | Keyboard / screen reader |
| --- | --- | --- | --- |
| Loading | "Loading 3D viewer..." (capability check runs after mount; lazy three.js chunk) | `viewer3d.loading` | `role=status` |
| Empty | Neutral model, "No region selected", "No regions with findings." | `viewer3d.none`, `viewer3d.empty` | canvas is `role=img` with label; not focusable |
| Partial / Full | Regions coloured by the light-theme hex; region buttons "label: severity"; detail card on selection | `viewer3d.listTitle`, `viewer3d.detail`, `viewer.severity.*` | list buttons `aria-pressed`; detail in `aria-live=polite`; Escape clears; "Clear selection" button |
| Error | GLB or context failure caught by the boundary: auto-switch to 2D with reason | `viewer3d.reason.error` | reason in `role=status` |

Controls: manual toggle `viewer3d.switchTo2d` / `switchTo3d` (button, 44 px target). Drag and zoom have no on-screen button alternative yet (gap 5).

### 4.1 Fallback rules (3D to 2D)
Order of checks (`decideViewer`): no WebGL, then Save-Data or `prefers-reduced-data`, then cores < 4, then memory < 4 GB; unknown cores/memory do not block. At runtime: render error (GLB load, context loss) and FPS < 30 over 3 s after a 1 s warm-up. A manual choice of 3D disables the FPS fallback; a manual 2D choice is kept.

| Reason | Key (existing) | EN |
| --- | --- | --- |
| noWebgl | `viewer3d.reason.noWebgl` | Showing the 2D map because 3D is not available on this device. |
| saveData | `viewer3d.reason.saveData` | Showing the 2D map because data saving is on. |
| lowCores, lowMemory | `viewer3d.reason.lowCores`, `.lowMemory` | Showing the 2D map because this device may be too slow for 3D. |
| lowFps | `viewer3d.reason.lowFps` | Switched to the 2D map because the 3D view was running slowly. |
| error | `viewer3d.reason.error` | Switched to the 2D map because the 3D view could not load. |
| manual2d, manual3d | `viewer3d.reason.manual2d`, `.manual3d` | Showing the 2D map. / Showing the 3D view. |

The fallback keeps the list, selection note and illustration note. Reason text is a polite status, never an error tone.

## 5. Timeline compare (`TimelineScreen`, `ProfileBodyScreen`)

| State | What shows | Copy keys | Keyboard / screen reader |
| --- | --- | --- | --- |
| Loading | status line | `timeline.loading` | `role=status` |
| Error | danger Alert; retry by reload | `timeline.loadError` | alert role from `Alert` |
| Empty | "No confirmed findings yet..." | `timeline.empty` | |
| One visit | explanation + that visit's body view | `timeline.oneVisit`, `timeline.latestVisit` | |
| Two or more | two labelled selects, two 2D maps, differences (added / removed / both), measurements table with caption | `timeline.pickBefore/After`, `timeline.diff.*`, `timeline.diffNote`, `timeline.obs*` | selects labelled; table has `scope` headers; region lists are text |
| Partial | undated visit "Date not listed"; a lab on one side shows "Not listed" | `timeline.undated`, `timeline.notListed` | |

Wording: differences never say better or worse (`timeline.diffNote`). Patient-reported findings and metastasis follow section 1.2 inside both maps (gaps 1, 2).

## 6. Sharing
`features/sharing` is empty at this commit; no viewer state is specified for shared views. Open: a recipient sees the same legend and illustration note; revisit when merged.

## 7. Gaps between spec and code
1. patient_reported has no styling or "you described" label in any viewer; `toRegions` maps a null severity to `reference`, so a self-reported item would look like a grey clinical finding (HZ-011, BR-040). Key `viewer.patientReported` is absent.
2. Metastasis: `is_metastasis` is parsed (`lib/api/findings.ts`) but unused by viewers; no "stated in your record" label, no BR-046 summary mode, no BR-049 neutral-style check.
3. Only `spread` and `reference` have a non-colour outline cue in `BodyMap2D`; the other four rely on adjacent text. Odontogram cues are complete (dash, cross, ring).
4. `mild` light hex is 2.9:1 on white (< 3:1 for graphics); fill opacity 0.75 lowers it further. Needs a token decision.
5. No on-screen rotate / zoom / reset buttons for 3D (WCAG 2.5.7); the wireframe keyboard set (arrows, +/-, R) is not implemented, only Escape.
6. `BodyMap2D` is always rendered with `side="front"`; no front/back switch, so back-only regions cannot be shown.
7. The odontogram has no route or screen; users cannot reach it yet. Caries reuses `severity.moderate` (D79 question).
8. Odontogram `implant` uses `severity.monitor` (green); `filled` and `missing` use `reference`; colour may imply a severity the record did not state.
9. 3D uses light-theme hex only (`severityColor`); dark mode would show light-theme colours on a dark surface.
10. Keys used by the wireframe but missing from messages: `viewer.error`, `viewer.conflict`, `viewer.resected`, `viewer.sideUnknown`, `viewer.patientReported`, `finding.unmapped`, `onco.spreadLayer`, `common.loading`. Wireframe fallback key `viewer.noWebgl` is superseded by `viewer3d.reason.*`.
11. No visible severity legend component exists; severity text appears only per item.
12. No error state or Retry in `BodyMap2D` or `Odontogram`; `ProfileBodyScreen` has no conflict banner for two disagreeing sources.
13. Unknown region codes are dropped silently from the list (callback only); a finding that cannot be placed should be listed as unmapped (HZ-002).
14. GLB models are stylised placeholders, not real anatomy, and the UI does not say so.
