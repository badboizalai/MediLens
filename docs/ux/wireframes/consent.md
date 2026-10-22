# Screen Spec: Consent

| Field | Value |
| --- | --- |
| Route | /onboarding/consent |
| Rules | BR-002 (consent before first upload; re-consent on new version) |
| Primary action | Agree and continue |
| Personas | Patient, caregiver |

## Purpose
Obtain explicit, informed consent to process health data before any upload. Re-shown when the consent version changes.

## Wireframe (mobile 360 px)
```
+--------------------------------+
| MediLens            [VI | EN]  |
+--------------------------------+
| Before you start               |
|  - we show and explain your    |
|    record                      |
|  - we never diagnose           |
|  - no training on your data    |
|    unless you opt in           |
| [Read full privacy notice >]   |
|                                |
| [ ] Health-data consent (req.) |
| [ ] Research use (optional)    |
|                                |
| [ Agree and continue ]  (off   |
|   until required box ticked)   |
| [ Not now ]                    |
+--------------------------------+
```

## Components
| Component | Notes |
| --- | --- |
| Summary list | 3 plain-language bullets, then link to full notice |
| Checkbox (required) | Not pre-ticked; separate from optional |
| Checkbox (optional) | Separate opt-in (BR-034); declining never blocks use |
| Primary button | Disabled until required box ticked, with reason text |

## States
| State | What the user sees | Copy key |
| --- | --- | --- |
| Default | Both boxes unticked, button disabled | consent.health |
| Loading | Button spinner, `aria-busy`, no double submit | common.saving |
| Error | Inline banner, retry, nothing recorded | consent.error |
| Re-consent | Banner "terms changed", change summary, same form | consent.reconsent |
| Declined | "Not now" returns to Landing; upload not possible | consent.declined |
| Empty | n/a (static form) | |

## Copy (VI / EN)
| Key | VI | EN |
| --- | --- | --- |
| consent.health | Tôi đồng ý cho MediLens xử lý dữ liệu sức khỏe của tôi để hiển thị và giải thích hồ sơ. | I agree that MediLens may process my health data to display and explain my records. |
| consent.research | (Tùy chọn) Tôi đồng ý cho dùng dữ liệu đã ẩn danh để cải thiện MediLens. | (Optional) I agree to use de-identified data to improve MediLens. |
| consent.cta | Đồng ý và tiếp tục | Agree and continue |
| consent.reconsent | Điều khoản đã thay đổi. Vui lòng xem và đồng ý lại. | Our terms changed. Please review and agree again. |
| consent.error | Chưa lưu được lựa chọn của bạn. Hãy thử lại. | We couldn't save your choice. Please try again. |
| consent.declined | Bạn cần đồng ý để tải hồ sơ lên. Bạn có thể quay lại bất cứ lúc nào. | You need to agree to upload records. You can come back anytime. |

## Accessibility
- Focus order: language switch, summary, notice link, required checkbox, optional checkbox, Agree, Not now.
- Each checkbox has a visible label as its accessible name; "required" is text, not colour alone.
- Disabled button explains why via `aria-describedby`. Errors announced via `aria-live="polite"`.
- Targets 44x44 px.

## Open questions
- Final legal text from regulatory-privacy-officer (Law 91/2025/QH15).
