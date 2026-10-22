# Screen Spec: Settings

| Field | Value |
| --- | --- |
| Route | /app/settings |
| Rules | BR-004 (lockout), BR-032 (export and delete: soft now, hard after 30 days), BR-034 (no training without opt-in), BR-002 |
| Primary action | none (data-subject actions: Export, Delete) |
| Personas | Patient, caregiver |

## Purpose
Manage language, security (MFA, sessions), consent choices, and data rights (export, delete account).

## Wireframe (desktop 1280 px)
```
+---------------------------------------------------------------+
| Settings                                                      |
+----------------+----------------------------------------------+
| Profile        | Language   ( VI ) ( EN )                     |
| Security       |----------------------------------------------|
| Privacy        | Security                                     |
| Your data      |  MFA: On          [Manage]                   |
|                |  Sessions: This device (now)                 |
|                |            Phone, 20/10/2026  [Sign out]     |
|                |----------------------------------------------|
|                | Privacy                                      |
|                |  [x] Health-data consent (required)          |
|                |  [ ] Research use (optional)  [Save]         |
|                |----------------------------------------------|
|                | Your data                                    |
|                |  [ Export my data ]                          |
|                |  [ Delete my account ]                       |
+----------------+----------------------------------------------+
```
Mobile: sections as a vertical list, each opens its own page.

## Components
| Component | Notes |
| --- | --- |
| Language switch | Applies immediately, persists |
| MFA card | Status text, manage flow |
| Sessions list | Device, date, Sign out per session and "sign out all" |
| Consent toggles | Required consent shows what withdrawing means; optional is a separate opt-in |
| Export button | Starts a job; link appears when ready |
| Delete dialog | Explains soft delete then hard delete after 30 days, requires typing a confirm word and re-authentication |

## States
| State | Trigger | What the user sees | Copy key |
| --- | --- | --- | --- |
| Loading | Fetching settings | Skeleton sections | common.loading |
| Empty | No other sessions | "Only this device" | settings.onlyThis |
| Export pending | Export requested | Status "preparing", can leave | settings.exportPending |
| Export ready | Job done | Download link with expiry | settings.exportReady |
| Delete confirm | Delete pressed | Dialog with consequences | settings.deleteConfirm |
| Delete pending | Deleted (soft) | Signed out; message of 30-day window | settings.deleted |
| Error | Save/export/delete failed | Banner and Retry; nothing changes silently | settings.error |
| Lockout | Too many failed attempts (BR-004) | Time-based lock message on sign-in | settings.locked |
| Permission denied | Session expired | Redirect to sign-in with warning before expiry | settings.session |

## Copy (VI / EN)
| Key | VI | EN |
| --- | --- | --- |
| settings.onlyThis | Bạn chỉ đang đăng nhập trên thiết bị này. | You are signed in on this device only. |
| settings.exportPending | Đang chuẩn bị dữ liệu của bạn. Bạn có thể rời trang này. | Preparing your data. You can leave this page. |
| settings.exportReady | Dữ liệu đã sẵn sàng để tải xuống. | Your data is ready to download. |
| settings.deleteConfirm | Tài khoản sẽ bị khóa ngay và dữ liệu bị xóa vĩnh viễn sau 30 ngày. Bạn chắc chắn chứ? | Your account is locked now and data is permanently deleted after 30 days. Are you sure? |
| settings.deleted | Đã gửi yêu cầu xóa. Bạn có 30 ngày trước khi dữ liệu bị xóa vĩnh viễn. | Deletion requested. You have 30 days before data is permanently removed. |
| settings.optIn | Cho phép dùng dữ liệu đã ẩn danh để cải thiện MediLens (tùy chọn). | Allow de-identified data to improve MediLens (optional). |
| settings.error | Chưa lưu được thay đổi. Hãy thử lại. | We couldn't save your changes. Please try again. |
| settings.session | Phiên sắp hết hạn. Bạn có muốn tiếp tục không? | Your session is about to expire. Stay signed in? |

## Accessibility
- Section nav is a landmark with `aria-current`; focus order follows visual order.
- Dialogs: focus trap, Esc closes, destructive action not the default focus; confirm word input is labelled.
- Session timeout warning with an extend option (no hidden time limit).
- Authentication without cognitive test: passkeys and password managers allowed (3.3.8).
- Statuses via `aria-live`; targets 44x44 px.
