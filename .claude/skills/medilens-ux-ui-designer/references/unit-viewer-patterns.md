# Unit Viewer Patterns

## Generic body viewer
- Canvas area (60–70% width desktop, full width mobile) + side/bottom sheet detail panel.
- Toolbar: 2D/3D toggle, camera presets (front, back, left, right), layers (skin, muscle, skeleton, organs, vessels, lymph), x-ray slider, reset, findings list.
- Findings list (always available): grouped by Unit → Region, each with severity chip, date, source link.
- Timeline bar (bottom): dates of encounters; selecting two dates enables side-by-side compare.

## Dental (FDI)
- 2D: two arches (upper 18→11 | 21→28, lower 48→41 | 31→38), each tooth with 5 surfaces (O, M, D, B, L) clickable; deciduous mode 51–85 toggle.
- Status icons: caries (dot on surface), missing (dashed outline), filling (filled surface, neutral colour), implant (screw icon), root canal (line in root).
- 3D: jaw model, rotate to see buccal/lingual; tooth highlight matches 2D selection.
- Detail panel: tooth name ("Răng hàm lớn thứ nhất hàm dưới bên trái — răng 36"), surfaces affected, record quote, care questions.

## Cardiology
- 3D heart with chambers, valves, coronary arteries; cutaway toggle to show inside chambers.
- 2D: schematic heart (4 chambers + valves) and coronary tree.
- Observations panel: EF%, BP, lipid labs as small trend charts with reference band.
- Valve findings use stenosis/regurgitation icons; coronary stenosis as a narrowed segment with % label if stated.

## Oncology
- Full body with organ layer on; primary tumour as a filled region with size label if stated.
- Lymph node involvement as small nodes highlighted in the relevant station.
- Metastasis: solid curved line primary → site **only if stated**; legend item "Di căn (theo hồ sơ)".
- "Possible spread" educational layer: off by default, dashed grey lines, label "Thông tin tham khảo, không phải tình trạng của bạn".
- Staging card: TNM and stage as written, with plain-language explanation of each letter; no survival numbers.
- Treatment events on timeline (surgery, chemo cycles, radiotherapy) as markers.

## Special anatomy and sources (plan section 27)
- Resected organ: hidden or 15% ghost + label "đã cắt bỏ (theo hồ sơ)"; never coloured.
- Implant/device: glyph + name on hover; legend entry "thiết bị / device".
- Precision: organ-level and system-level findings use outline/badge, not a precise spot; "không rõ bên / side not stated" when laterality is unknown.
- Patient-reported findings: neutral grey style, speech-bubble icon, "bạn mô tả / you described".
- CT-derived anatomy (v2): watermark "minh họa từ CT của bạn, không phải kết quả đọc phim"; template vs personal toggle.
- Conflicts between sources: amber banner naming both sources, never a silent overwrite.
All new states are reviewed with the clinical safety officer before build.

## Responsive rules
- < 768 px: 2D default, detail as bottom sheet, findings list as tab.
- ≥ 1024 px: side panel; 3D default if WebGL capable.
- Touch: one-finger rotate, two-finger pinch zoom/pan; double-tap reset.
