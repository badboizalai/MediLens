# Screen Spec: Timeline

| Field | Value |
| --- | --- |
| Route | /app/timeline |
| Rules | BR-013 (confirmed data only), BR-020 (severity colour + text), BR-042 |
| Primary action | Compare dates |
| Personas | Patient, caregiver |

## Purpose
Show encounters and findings over time and let the user compare two dates side by side. It shows what the records say changed; it does not interpret trends or predict.

## Wireframe (desktop 1280 px)
```
+---------------------------------------------------------------+
| Hình minh họa giúp bạn hiểu hồ sơ, không thay thế ý kiến bác sĩ|
+---------------------------------------------------------------+
| Timeline   Filter: [All units v]                              |
| o----------o----------o----------o                            |
| 03/2025   09/2025   12/2025   03/2026   (select 2 dates)      |
+------------------------------+--------------------------------+
| 09/2025                      | 03/2026                        |
|  (body 2D, regions coloured) |  (body 2D, regions coloured)   |
|  Tooth 36 <! Cần chú ý>      |  Tooth 36 <! Cần chú ý>        |
|                              |  Tooth 37 <New: Theo dõi>      |
+------------------------------+--------------------------------+
| Changes recorded: 1 new, 0 resolved, 0 changed   [List view]  |
+---------------------------------------------------------------+
```
Mobile: stacked compare with a date switcher; list view as a tab.

## Components
| Component | Notes |
| --- | --- |
| Timeline bar | Encounter dots keyboard-selectable; treatment events as markers |
| Compare panes | Two 2D bodies, synchronised zoom |
| Change summary | Counts new / resolved / changed per the records, text only |
| List view | Text equivalent of the panes |
| SeverityChip | Colour + icon + text |

## States
| State | Trigger | What the user sees | Copy key |
| --- | --- | --- | --- |
| Loading | Fetching encounters | Skeleton bar and panes | common.loading |
| Empty | No confirmed encounters | Explanation and Upload button | timeline.empty |
| Single encounter | Only one date | One pane; "add another record to compare" | timeline.single |
| Error | Fetch failed | ErrorState with Retry | timeline.error |
| Permission denied | Not the owner | Not-found | common.notFound |

## Copy (VI / EN)
| Key | VI | EN |
| --- | --- | --- |
| timeline.empty | Chưa có lần khám nào được xác nhận. Tải hồ sơ lên để bắt đầu. | No confirmed visits yet. Upload a record to begin. |
| timeline.single | Mới có một lần khám. Thêm hồ sơ khác để so sánh. | Only one visit so far. Add another record to compare. |
| timeline.pick | Chọn hai ngày để so sánh. | Pick two dates to compare. |
| timeline.changes | Theo hồ sơ: {new} mục mới, {resolved} mục đã ghi nhận hết, {changed} mục thay đổi. | Per your records: {new} new, {resolved} no longer listed, {changed} changed. |
| timeline.error | Chưa tải được dòng thời gian. Hãy thử lại. | We couldn't load the timeline. Please try again. |

Wording rule: "per your records" only; no words like "worse", "improved", "will".

## Accessibility
- Timeline is a listbox of dates; arrows move, Space/Enter selects (max 2); selection announced via `aria-live`.
- Compare panes labelled "Ngày {date}"; list view gives the same data as text.
- Severity never colour alone; targets 44x44 px; reflow at 320 px.
