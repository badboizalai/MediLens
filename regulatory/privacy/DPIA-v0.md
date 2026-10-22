# DPIA v0 (đánh giá tác động xử lý dữ liệu cá nhân) — MediLens v1

> **Draft — educational, not legal advice; requires human DPO/REG sign-off.**
> Người soạn là một agent AI. Mọi chỗ không chắc chắn được đánh dấu `VERIFY:`. Theo mẫu security skill `dpia-template.md` và checklist `dpia-otia-checklist.md`. Phải hoàn tất trước khi xử lý dữ liệu thật; nộp trong 60 ngày kể từ khi bắt đầu xử lý (Form 10, `VERIFY:` số mẫu).

| Field | Value |
| --- | --- |
| Phiên bản / ngày | v0 / 2026-10-23 |
| Liên kết | [data-inventory.md](data-inventory.md), [OTIA-decision.md](OTIA-decision.md), [../RDR-001.md](../RDR-001.md) |
| Review | Hằng năm hoặc khi thay đổi lớn (nhà cung cấp, mục đích, thêm CT/v2) |

## 1. Bên kiểm soát / xử lý
- Controller: `VERIFY:` pháp nhân/cá nhân vận hành (hiện là dự án học tập một người).
- DPO / người chịu trách nhiệm: `VERIFY:` tên và liên hệ; người thật đủ điều kiện trước khi có dữ liệu thật.
- Processors: AWS, nhà cung cấp LLM/OCR/email (xem data-inventory.md).

## 2. Mô tả xử lý
- Mục đích: giúp người dùng hiểu hồ sơ của chính họ (upload, OCR + LLM trích xuất, review, viewer). Chỉ minh họa/giải thích, không chẩn đoán (BR-042). <!-- claims-ok -->
- Chủ thể: người lớn, trẻ em qua người giám hộ (BR-001), người được chia sẻ (bác sĩ, chỉ xem).
- Dữ liệu: C4 PHI, C3 PII (xem data-inventory.md D1-D14).
- Nguồn: người dùng tải lên. Nơi xử lý: AWS Singapore, LLM `VERIFY:`.

## 3. Căn cứ pháp lý
Đồng ý rõ ràng, tách theo mục đích (BR-002), ghi phiên bản + thời điểm; có thể rút lại. Opt-in riêng cho đánh giá/huấn luyện (BR-034). Trẻ em: consent của người giám hộ. `VERIFY:` ngoại lệ và yêu cầu hình thức consent trong NĐ 356/2025.

## 4. Cần thiết và tương xứng
Tối thiểu hóa: không lưu số định danh; chỉ trường cần cho viewer. Chính xác: người dùng xác nhận mọi trích xuất; `ai_value` và `user_value` tách riêng (DAT-03). Lưu giữ theo plan §14.3. Giới hạn mục đích: không huấn luyện nếu chưa opt-in.

## 5. Luồng dữ liệu và chuyển ra nước ngoài
Browser → BFF → PHI Service → S3/Clinical DB (Singapore) → AI Worker (không internet) → AI Gateway (redact) → LLM. Chuyển ra nước ngoài: **cần OTIA** (xem OTIA-decision.md).

## 6. Rủi ro và kiểm soát
Likelihood (L) và Impact (I): 1 thấp, 2 vừa, 3 cao. Điểm = L x I. Mức đánh giá là chủ quan của bản nháp, `VERIFY:` bởi DPO.

| ID | Risk to data subject | L | I | Score | Controls | Residual |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | Rò rỉ PHI (lộ DB/S3, cấu hình sai) | 2 | 3 | 6 | KMS CMK, mã hóa trường, PHI Service duy nhất, RLS, Block Public Access (SEC-DP-01..04), kiểm toán đọc | Vừa |
| R2 | Truy cập trái phép/IDOR giữa người dùng | 2 | 3 | 6 | Authz mọi endpoint + test, Policy & Consent, break-glass có cảnh báo | Thấp-vừa |
| R3 | PHI/PII lọt vào log, trace, prompt | 2 | 3 | 6 | Redaction middleware + quét log (SEC-DP-06), redact trước LLM (SEC-AI-02, recall ≥ 99%) | Vừa |
| R4 | Nhà cung cấp LLM/OCR giữ hoặc huấn luyện trên dữ liệu | 2 | 3 | 6 | DPA, điều khoản không huấn luyện, allowlist mô hình, vendor assessment | Vừa, tới khi có hợp đồng |
| R5 | Chuyển ra nước ngoài không có OTIA/consent | 3 | 2 | 6 | OTIA trong 60 ngày, consent nêu rõ, không dùng dữ liệu thật trước | Thấp sau khi nộp |
| R6 | Prompt injection qua nội dung hồ sơ | 2 | 2 | 4 | SEC-AI-01, OCR text là dữ liệu, kiểm thử 50 ảnh độc | Thấp |
| R7 | Thông tin sai hiển thị (trích xuất/vị trí sai) gây hiểu lầm | 2 | 3 | 6 | Review bắt buộc của người dùng, `ai_value`/`user_value`, hiển thị độ tin cậy, CSO duyệt | Vừa |
| R8 | Tổn thương tâm lý (hình ảnh ung thư, từ ngữ đáng sợ) | 2 | 2 | 4 | Giọng văn trấn an, CSO duyệt, không tiên lượng/liều (BR-022/023) | Thấp <!-- claims-ok --> |
| R9 | Xóa không triệt để (bản sao, backup, cache) | 2 | 2 | 4 | Crypto-shredding (SEC-DP-08), DSR runbook, backup hết hạn | Thấp-vừa |
| R10 | Tái định danh từ analytics/dữ liệu tặng | 1 | 3 | 3 | HMAC khóa riêng, bỏ C3, k ≥ 10 (DAT-08/09), khử định danh có QA | Thấp |
| R11 | Dữ liệu trẻ em xử lý không có consent giám hộ | 1 | 3 | 3 | BR-001, kiểm tra tuổi, bản ghi consent | Thấp |
| R12 | Vi phạm không được báo trong 72 giờ | 2 | 2 | 4 | Kế hoạch ứng phó sự cố, mẫu Form 08, diễn tập | Thấp |
| R13 | Phân biệt đối xử nếu hồ sơ bị chia sẻ/lộ cho bên thứ ba (bảo hiểm, nơi làm việc) | 1 | 3 | 3 | Chia sẻ có phạm vi + hết hạn, watermark (SEC-DP-09), không chia sẻ mặc định | Thấp |
| R14 | Dữ liệu thật dùng ở dev/staging | 2 | 3 | 6 | SCP chặn sao chép snapshot (SEC-DP-07), dữ liệu tổng hợp, kiểm tra CI | Thấp |

## 7. Quyền của chủ thể dữ liệu
Truy cập, chỉnh sửa, xóa, hạn chế, phản đối, rút consent, di chuyển dữ liệu qua quy trình DSR (BR-036, PB-06) có xác minh danh tính. `VERIFY:` thời hạn trả lời theo NĐ 356/2025.

## 8. Rủi ro còn lại và chấp nhận
Chưa chấp nhận. Mục tiêu: không rủi ro nào ở mức cao (score ≥ 6) còn lại khi vào dữ liệu thật; R1, R3, R4, R7, R14 cần bằng chứng triển khai (Security Evidence Pack) trước khi ký.

| Người ký | Vai trò | Ngày | Quyết định |
| --- | --- | --- | --- |
| `____` | DPO | | Chờ |
| `____` | REG | | Chờ |

## 9. Lịch rà soát và hồ sơ nộp
Rà soát hằng năm hoặc khi đổi nhà cung cấp/mục đích/thêm CT. Nộp hồ sơ DPIA trong 60 ngày kể từ khi bắt đầu xử lý dữ liệu thật: ngày bắt đầu `____`, hạn nộp `____`. `VERIFY:` cơ quan tiếp nhận và quy trình nộp.

## 10. Câu hỏi mở
- Chọn nhà cung cấp LLM/OCR/email cuối cùng và vùng.
- Căn cứ pháp lý chính xác cho D4, D5, D8-D10.
- Dữ liệu giả danh có còn là dữ liệu cá nhân không.
