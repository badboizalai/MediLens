# Screen Spec: Upload

| Field | Value |
| --- | --- |
| Route | /app/upload |
| Rules | BR-010/011 (JPG/PNG/HEIC/PDF, max 20 MB, max 30 pages, reject blurry/low-res), BR-041 |
| Primary action | Choose or take photo |
| Personas | Patient, caregiver, low digital literacy |

## Purpose
Get a readable record into the system with minimal friction and clear capture guidance. After upload the user may leave; processing continues in the background.

## Wireframe (mobile 360 px)
```
+--------------------------------+
| < Back            Upload       |
+--------------------------------+
| Add a medical record           |
|  +--------------------------+  |
|  |  [ Take photo ]          |  |
|  |  [ Choose file ]         |  |
|  |  or drop a file here     |  |
|  +--------------------------+  |
| JPG PNG HEIC PDF, up to 20 MB, |
| 30 pages                       |
| Tips: good light, phone flat   |
|  above the page, whole page in |
|  frame            [Examples]   |
|                                |
| Selected: lab_2026.pdf  [x]    |
| [ Upload ]                     |
+--------------------------------+
```
Desktop: two columns, drop zone left, capture tips right.

## Components
| Component | Notes |
| --- | --- |
| FileDropzone | A button equivalent always present (no drag-only, WCAG 2.5.7) |
| CaptureTips | Inline, collapsible, synthetic example images |
| FilePreview list | Name, size, page count, remove |
| Quality warning | After quality check; offers Retake |
| Describe-in-words link | Secondary; creates patient_reported text (BR-040) |

## States
| State | Trigger | What the user sees | Copy key |
| --- | --- | --- | --- |
| Empty | First visit | Dropzone plus tips | upload.hint |
| Loading | Upload in progress | Per-file progress bar, cancel | upload.progress |
| Processing | Upload done | Stepper queued/reading/extracting; may leave page | upload.processing |
| Quality warning | Blurry/low-res | Warning with Retake; rejected images cannot continue | upload.blurry |
| Error: type | Wrong format | Names allowed formats | upload.badType |
| Error: size | Over 20 MB / 30 pages | States the limit and what to do | upload.tooLarge |
| Error: network | Connection lost | Retry keeps the selected file | upload.retry |
| Emergency text | Description mentions emergency signs (BR-041) | 115 message shown before anything else | explain.emergency |

## Copy (VI / EN)
| Key | VI | EN |
| --- | --- | --- |
| upload.hint | Chụp hoặc chọn hồ sơ của bạn (JPG, PNG, HEIC, PDF, tối đa 20 MB, 30 trang). | Take or choose your record (JPG, PNG, HEIC, PDF, up to 20 MB, 30 pages). |
| upload.blurry | Ảnh hơi mờ. Hãy chụp lại nơi đủ sáng, giữ máy song song với tờ giấy. | The photo is a bit blurry. Retake it in good light, holding the phone parallel to the page. |
| upload.processing | Đang đọc hồ sơ… thường mất dưới 2 phút. | Reading your record… usually under 2 minutes. |
| upload.leave | Bạn có thể rời trang này, chúng tôi sẽ báo khi xong. | You can leave this page; we'll tell you when it's done. |
| upload.badType | Định dạng này chưa được hỗ trợ. Hãy dùng JPG, PNG, HEIC hoặc PDF. | This format isn't supported. Please use JPG, PNG, HEIC or PDF. |
| upload.tooLarge | Tệp quá lớn (tối đa 20 MB, 30 trang). Hãy chia nhỏ hoặc chụp lại. | The file is too large (max 20 MB, 30 pages). Split it or retake. |
| upload.retry | Mất kết nối. Nhấn Thử lại để tiếp tục. | Connection lost. Press Retry to continue. |
| explain.emergency | Nếu bạn đang đau ngực, khó thở hoặc có nguy hiểm tức thời, hãy gọi 115 ngay. | If you have chest pain, trouble breathing or are in immediate danger, call 115 now. |

## Accessibility
- Focus order: tips toggle, Take photo, Choose file, file list, Upload.
- Progress via `role="progressbar"` plus `aria-live="polite"` status text; status never colour-only.
- Camera and file controls labelled and keyboard operable.
- Errors linked with `aria-describedby` to the control.

## Open questions
- HEIC conversion location (client vs server): frontend-engineer.
