# Screen Spec: Share

| Field | Value |
| --- | --- |
| Route | /app/sharing |
| Rules | BR-030/031 (scoped, time-limited default 7 / max 90 days, revocable, signed-in recipients only), BR-035 (audit) |
| Primary action | Create share |
| Personas | Patient, caregiver, doctor (recipient) |

## Purpose
Let the user give a doctor or family member limited, expiring, revocable access to chosen parts of their record.

## Wireframe (mobile 360 px)
```
+--------------------------------+
| < Back           Sharing       |
+--------------------------------+
| New share                      |
| Recipient email                |
| {doctor@example.test        }  |
| What to share                  |
|  [x] Dental findings           |
|  [x] Heart findings            |
|  [ ] Original files            |
| Valid for  ( 7 days v )  max 90|
| Access expires after 7 days.   |
| You can revoke it anytime.     |
| [ Create share ]               |
+--------------------------------+
| Active shares                  |
|  dr.a@example.test  Dental     |
|  expires 30/10/2026  [Revoke]  |
| Past shares (expired/revoked)  |
+--------------------------------+
```

## Components
| Component | Notes |
| --- | --- |
| ShareScopePicker | Checkboxes by Unit and by file; nothing pre-ticked |
| Expiry selector | Default 7, max 90 days |
| Confirm dialog | Summary of recipient, scope, expiry before creating |
| Share list | Active, expired, revoked with status text |
| Revoke button | Confirm dialog, immediate effect |

## States
| State | Trigger | What the user sees | Copy key |
| --- | --- | --- | --- |
| Empty | No shares | Explanation and the form | share.empty |
| Loading | Creating / fetching | Button spinner, list skeleton | common.loading |
| Validation error | Bad email, no scope, expiry over 90 | Inline error linked to the field | share.invalid |
| Recipient not found | Recipient has no account | Message: recipient must sign in; invite option | share.needAccount |
| Error | Create or revoke failed | Banner, Retry | share.error |
| Expired / Revoked | Past shares | Status text label, no actions except delete from list | share.expired |
| Permission denied | Not the owner | Not-found | common.notFound |
| Success | Created | Toast and the share shown in Active | share.created |

## Copy (VI / EN)
| Key | VI | EN |
| --- | --- | --- |
| share.expiry | Quyền xem sẽ tự hết hạn sau {days} ngày. Bạn có thể thu hồi bất cứ lúc nào. | Access expires after {days} days. You can revoke it anytime. |
| share.empty | Bạn chưa chia sẻ hồ sơ nào. | You haven't shared anything yet. |
| share.invalid | Hãy nhập email hợp lệ, chọn ít nhất một mục và thời hạn tối đa 90 ngày. | Enter a valid email, pick at least one item, and a period of up to 90 days. |
| share.needAccount | Người nhận cần đăng nhập MediLens để xem. | The recipient must sign in to MediLens to view. |
| share.confirm | Chia sẻ {scope} với {email} trong {days} ngày? | Share {scope} with {email} for {days} days? |
| share.revokeConfirm | Thu hồi quyền xem của {email} ngay bây giờ? | Revoke access for {email} now? |
| share.created | Đã tạo chia sẻ. | Share created. |
| share.error | Chưa thực hiện được. Hãy thử lại. | That didn't work. Please try again. |
| share.expired | Đã hết hạn | Expired |

## Accessibility
- Focus order: recipient, scope checkboxes, expiry, Create; dialogs trap focus and return it on close.
- Scope group is a `fieldset` with `legend`; errors linked via `aria-describedby`; status via `aria-live`.
- Status (active/expired/revoked) in text plus icon, not colour alone.
- Date shown in local format; targets 44x44 px.
