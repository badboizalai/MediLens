# Screen Spec: Viewer (2D/3D body viewer)

| Field | Value |
| --- | --- |
| Route | /app/viewer (Unit viewer: /app/viewer/[unit]) |
| Rules | BR-013, BR-015, BR-020 (severity colour + text), BR-021, BR-040, BR-042 |
| Primary action | Select region |
| Personas | Patient, caregiver |
| Reviewers | clinical-safety-officer (wording, severity labels) |

## Purpose
Illustrate where confirmed findings are on the body. It is an illustration to help understanding, not a diagnosis.

## Wireframe (desktop 1280 px)
```
+---------------------------------------------------------------+
| Hình minh họa giúp bạn hiểu hồ sơ, không thay thế ý kiến bác sĩ|  <- DisclaimerBar (always visible)
+---------------------------------------------------------------+
| [2D|3D] [Front Back Left Right] Layers v  X-ray --o--  [Reset]|
+-------------------------------------+-------------------------+
|                                     | Findings (4)            |
|            .---.                    | Dental                  |
|           ( o o )  <region 36>      |  > Tooth 36  <! Cần chú ý>|
|           /|   |\                   |    12/03/2026  Source:lab|
|             |_|                     | Heart                   |
|            /   \                    |  > Mitral valve <Theo dõi>|
|     (canvas, keyboard focusable)    | Unmapped (1)            |
|                                     |  > "đau vùng khác"      |
|                                     | [Open detail panel]     |
+-------------------------------------+-------------------------+
| Timeline: o--------o------------o   (select 2 dates to compare)|
+---------------------------------------------------------------+
```
Mobile: 2D default, canvas full width, detail as bottom sheet, findings list as a tab.

## Components
| Component | Notes |
| --- | --- |
| DisclaimerBar | `disclaimer.short`, not dismissible |
| Toolbar | 2D/3D, camera presets, layers, x-ray, reset; button alternatives to drag (WCAG 2.5.7) |
| Body canvas | Regions keyed by `region_code`; each has a title |
| Findings list | Text equivalent of canvas; grouped Unit > Region; SeverityChip, date, SourceBadge |
| SeverityChip | Colour + icon + text label (BR-020); patient_reported = neutral grey, speech-bubble, "bạn mô tả" (BR-040) |
| Special anatomy | Resected organ ghost + "đã cắt bỏ (theo hồ sơ)"; implant glyph; "không rõ bên" for unknown laterality |
| Detail panel | Record quote, meaning, questions for doctor, sources (see explain.md) |

## States
| State | Trigger | What the user sees | Copy key |
| --- | --- | --- | --- |
| Loading | Assets and findings loading | Silhouette skeleton, progress, list skeleton | common.loading |
| Empty | No confirmed findings | Plain body, "No findings yet", button to Upload | viewer.empty |
| Unmapped only | Findings without region | Body plain; items in list | finding.unmapped |
| WebGL fallback | No WebGL / low FPS | Auto 2D with notice and list | viewer.noWebgl |
| Error | Findings or asset failed | ErrorState, Retry, list still tried | viewer.error |
| Conflict | Two sources disagree | Amber banner naming both sources, no overwrite | viewer.conflict |
| Permission denied | Not the owner | Not-found page | common.notFound |

## Copy (VI / EN)
| Key | VI | EN |
| --- | --- | --- |
| disclaimer.short | Hình minh họa giúp bạn hiểu hồ sơ, không thay thế ý kiến bác sĩ. | This illustration helps you understand your record; it does not replace your doctor. |
| viewer.illustration | Đây là hình minh họa, không phải chẩn đoán. | This is an illustration, not a diagnosis. |
| viewer.empty | Chưa có thông tin nào được xác nhận. Hãy tải hồ sơ lên để bắt đầu. | Nothing confirmed yet. Upload a record to begin. |
| viewer.noWebgl | Thiết bị của bạn không hiển thị được 3D. Đang dùng hình 2D. | Your device can't show 3D. Using the 2D view. |
| viewer.error | Chưa tải được hình cơ thể. Danh sách bên dưới vẫn dùng được. | We couldn't load the body view. The list below still works. |
| viewer.conflict | Hai nguồn ghi khác nhau: {a} và {b}. Hãy hỏi bác sĩ để làm rõ. | Two sources differ: {a} and {b}. Ask your doctor to clarify. |
| viewer.resected | đã cắt bỏ (theo hồ sơ) | removed (per your record) |
| viewer.sideUnknown | không rõ bên | side not stated |
| viewer.patientReported | bạn mô tả | you described |
| onco.spreadLayer | Thông tin tham khảo, không phải tình trạng của bạn | Reference information, not your condition |

Severity chips always show a text label next to the colour; exact labels pending clinical-safety-officer. Wording rule: describe what the record says; never "you have", never advice on treatment, dose or outlook.

## Accessibility
- Keyboard: arrows rotate, +/- zoom, R reset, Tab through the findings list; focus ring at least 2 px, contrast 3:1.
- Findings list is the full text alternative; SVG regions have `<title>` in the current language.
- Severity not by colour alone; contrast 4.5:1 text, 3:1 graphics.
- `prefers-reduced-motion`: no auto-rotation, instant camera moves.
- Selection announced via `aria-live="polite"` ("Đã chọn răng 36").
- Target size 44x44 px for toolbar; sheet does not obscure focus (2.4.11).

## Open questions
- Severity label text for each of 5 colours (CSO).
- Oncology metastasis line and "possible spread" layer covered in the Unit viewer task, not here.
