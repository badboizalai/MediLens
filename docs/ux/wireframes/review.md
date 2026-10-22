# Screen Spec: Review

| Field | Value |
| --- | --- |
| Route | /app/documents/[id]/review |
| Rules | BR-012 (confidence < 0.7 must be confirmed), BR-013 (only confirmed data in viewer), BR-015 (unmapped, never guess) |
| Primary action | Confirm and show on the body |
| Personas | Patient, caregiver |

## Purpose
Let the user check what the AI extracted against the original, fix or remove wrong fields, and confirm. Nothing reaches the Viewer until confirmed.

## Wireframe (desktop 1280 px)
```
+--------------------------------------------------------------+
| < Documents   lab_2026.pdf   Extracted by AI - please check  |
+------------------------------+-------------------------------+
| ORIGINAL (zoom +/-, page 1/2)| EXTRACTED FIELDS   3 to check |
|  +------------------------+  | Finding text                  |
|  |  (scanned page; the    |  | {Sâu răng        }  [ok]      |
|  |   matching text is     |  | Location: tooth 36 (FDI)      |
|  |   outlined)            |  | ! We're not sure. Check it.   |
|  |                        |  | {Răng 36        } [Confirm]   |
|  |                        |  | Unmapped: "đau vùng khác"     |
|  +------------------------+  |  -> shown in the list         |
|                              | [Remove field] [Add field]    |
+------------------------------+-------------------------------+
| 3 fields left to check     [ Confirm and show on the body ]  |
+--------------------------------------------------------------+
```
Mobile: tabs "Original | Fields"; confirm bar sticky at bottom.

## Components
| Component | Notes |
| --- | --- |
| Original viewer | Pan/zoom; outline links to the selected field |
| ConfidenceField | Label, editable value, confidence flag (text + icon, not colour alone) |
| SourceBadge | "AI extracted" / "You edited" |
| Duplicate warning | Banner if the document seems already uploaded |
| Unmapped item | Listed with no body location (BR-015) |
| Sticky confirm bar | Counter of remaining low-confidence fields |

## States
| State | Trigger | What the user sees | Copy key |
| --- | --- | --- | --- |
| Loading | Fields fetching | Skeleton rows; original loads first | common.loading |
| Empty | No fields extracted | "Couldn't read fields": Add field or Re-upload | review.empty |
| Low confidence | Confidence < 0.7 | Field flagged; confirm disabled until checked | review.lowConfidence |
| Unmapped | No region | Neutral note, goes to list | finding.unmapped |
| Duplicate | Possible duplicate | Warning: Open existing / Continue | review.duplicate |
| Error: save | Confirm failed | Banner, edits kept locally, Retry | review.saveError |
| Permission denied | Not the owner | Not-found page, no existence leak | common.notFound |
| Success | Confirmed | Redirect to Viewer, toast | review.done |

## Copy (VI / EN)
| Key | VI | EN |
| --- | --- | --- |
| ai.label | Do AI trích xuất — vui lòng kiểm tra lại | Extracted by AI — please check |
| review.lowConfidence | Chúng tôi chưa chắc chắn về thông tin này. Bạn kiểm tra giúp nhé. | We're not sure about this one. Please check it. |
| review.confirmAll | Xác nhận và hiển thị lên cơ thể | Confirm and show on the body |
| finding.unmapped | Chưa xác định được vị trí trên cơ thể — hiển thị trong danh sách | Location not identified — shown in the list |
| review.remaining | Còn {n} mục cần kiểm tra | {n} items left to check |
| review.empty | Chưa đọc được mục nào. Bạn có thể thêm thủ công hoặc tải lại. | We couldn't read any fields. Add them manually or upload again. |
| review.duplicate | Hồ sơ này có vẻ đã được tải lên trước đó. | This record looks like it was uploaded before. |
| review.saveError | Chưa lưu được. Thay đổi của bạn vẫn còn, hãy thử lại. | Couldn't save. Your changes are kept; please try again. |
| review.done | Đã xác nhận. Đang mở hình cơ thể. | Confirmed. Opening the body view. |

## Accessibility
- Focus order: original controls, fields top to bottom, confirm bar. Selecting a field announces the linked page outline.
- Every field is a labelled input; confidence flag has text "Cần kiểm tra / Needs check".
- Counter and save result via `aria-live="polite"`.
- Original image alt: "Trang 1 của hồ sơ đã tải lên"; highlight uses outline plus label, not colour alone.
