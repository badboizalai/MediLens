# Data inventory v0 (bản ghi hoạt động xử lý dữ liệu)

> **Draft — educational, not legal advice; requires human DPO/REG sign-off.**
> Người soạn là một agent AI đóng vai Regulatory/Privacy officer. Mọi chỗ không chắc chắn về luật hoặc về nhà cung cấp được đánh dấu `VERIFY:`.
> Phiên bản v0, 2026-10-23. Nguồn: plan §14.1, §14.3, §24; `pdpl-obligations.md`. Phân loại C0-C4 theo plan §14.1; cột "PHI/PII/Other" là cách gọi theo luật.
> Trạng thái: **chưa có dữ liệu thật**. Dev/staging chỉ dùng dữ liệu tổng hợp (SEC-DP-07).

Pháp lý chung cho dữ liệu sức khỏe: đồng ý rõ ràng, theo từng mục đích (BR-002). `VERIFY:` điều khoản cụ thể của Luật 91/2025/QH15 / NĐ 356/2025 cho căn cứ pháp lý và các ngoại lệ.

## Bảng kiểm kê

| # | Data category | Examples | Class | PHI/PII/Other | Purpose | Legal basis | Source | Storage location | Retention | Processors / recipients |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | Ảnh/PDF hồ sơ gốc | Ảnh chụp, PDF bệnh án | C4 | PHI | OCR, review, xem lại | Consent sức khỏe (BR-002) | Người dùng tải lên | S3 `phi` (KMS `kms/phi`), ap-southeast-1; quarantine bucket 24 giờ | Đến khi người dùng xóa; xóa tài khoản: mềm 0 ngày, cứng 30 ngày | AWS (S3, KMS, GuardDuty) `VERIFY:` vùng |
| D2 | Văn bản OCR và kết quả trích xuất | OCR text, `ai_value` | C4 | PHI | Review, đánh giá | Consent sức khỏe | Pipeline OCR/LLM | Clinical DB (RDS PostgreSQL, ap-southeast-1), mã hóa trường theo bản ghi | Cùng tài liệu gốc | AWS RDS; OCR cục bộ (PaddleOCR/VietOCR) trong AI Worker; `VERIFY:` nhà cung cấp OCR cloud nếu dùng (Textract/Document AI) |
| D3 | Dữ liệu lâm sàng đã xác nhận | Chẩn đoán, xét nghiệm, BodyFinding, `user_value`, `region_code` | C4 | PHI | Viewer 2D/3D, timeline | Consent sức khỏe | Người dùng xác nhận | Clinical DB (RDS) | Cùng tài khoản | AWS RDS, PHI Service <!-- claims-ok --> |
| D4 | Danh tính | Họ tên, email, SĐT, ngày sinh | C3 | PII | Tài khoản, liên hệ | Hợp đồng/consent `VERIFY:` | Người dùng | Identity Link DB + `kms/identity` (ap-southeast-1); IdP Cognito/Keycloak `VERIFY:` | Đến khi người dùng yêu cầu xóa | AWS; nhà cung cấp email (SES/Resend) `VERIFY:` |
| D5 | Dữ liệu kỹ thuật | IP, user agent, device | C3 | PII | Bảo mật, chống lạm dụng | Lợi ích hợp pháp/consent `VERIFY:` | Trình duyệt | WAF/CloudWatch (đã che) | 30 ngày log; 1 năm bản đã che | AWS CloudWatch |
| D6 | Hồ sơ của người phụ thuộc (trẻ em) | Hồ sơ trẻ do người giám hộ tạo | C4 + C3 | PHI + PII | Như D1-D4 | Consent của người giám hộ (BR-001) | Người giám hộ | Như D1-D4 | Như D1-D4 | Như D1-D4 |
| D7 | Prompt/phản hồi LLM đã che | Văn bản đã redact PII | C2 (nguồn C4) | Có thể còn PHI gián tiếp | Trích xuất, giải thích, debug | Consent sức khỏe | AI Gateway | Cache khóa băm (KMS), log AI Gateway, ap-southeast-1 | 30 ngày | Nhà cung cấp LLM: dự kiến AWS Bedrock `VERIFY:` vùng/cross-region inference và mô hình; API ngoài (Claude/GPT/Gemini) nếu dùng `VERIFY:` |
| D8 | Nhật ký kiểm toán | Sự kiện truy cập (không PHI) | C2 | Other (có `subject_key`) | Điều tra, tuân thủ | Nghĩa vụ pháp lý/lợi ích hợp pháp `VERIFY:` | Hệ thống | CloudWatch 90 ngày; S3 Object Lock 3 năm | 3 năm | AWS |
| D9 | Log ứng dụng | Log đã redact | C2 | Other | Gỡ lỗi | Lợi ích hợp pháp `VERIFY:` | Hệ thống | CloudWatch | 30 ngày; 1 năm đã che | AWS |
| D10 | Analytics giả danh | Bảng gold HMAC, không C3 | C2 | Other (giả danh vẫn có thể là dữ liệu cá nhân `VERIFY:`) | Dashboard sản phẩm/AI | Consent riêng nếu cần `VERIFY:` | De-ID service | S3 analytics, Athena | 2 năm cuốn chiếu | AWS; chỉ công bố nhóm k ≥ 10 (DAT-09) |
| D11 | Dữ liệu tặng để đánh giá/huấn luyện | Hồ sơ đã khử định danh | C4 → C0/C2 | PHI đã khử định danh | Đánh giá/cải tiến mô hình | Opt-in riêng (BR-034, DAT-10) | Người dùng chọn tham gia | S3 `ml-*`, ap-southeast-1 | Đến khi rút consent; `VERIFY:` thời hạn trong Dataset Card | AWS; không gửi cho bên thứ ba |
| D12 | Backup | PITR, bản sao tháng | C4/C3 | PHI + PII | DR | Như nguồn | Hệ thống | AWS Backup, vault tài khoản riêng | PITR 35 ngày; bản tháng 1 năm; xóa bằng crypto-shredding (SEC-DP-08) | AWS |
| D13 | Dữ liệu tổng hợp | Hồ sơ giả, golden set | C0 | Other | Dev/test | Không áp dụng | Tự tạo | Repo, S3 `ml-*` | Theo dự án | Không |
| D14 | Nội dung công khai | Bài y khoa đã duyệt, asset 3D/2D | C1 | Other | Hiển thị | Không áp dụng | Nhóm dự án | S3 + CloudFront | Theo dự án | AWS |

## Nhà xử lý và nơi lưu trữ ngoài Việt Nam

| Processor | Vai trò | Dữ liệu | Vị trí | Ghi chú |
| --- | --- | --- | --- | --- |
| AWS | Hạ tầng: RDS, S3, KMS, SQS, CloudWatch, Backup | D1-D12 | **Singapore (ap-southeast-1) = ngoài Việt Nam** | `VERIFY:` DPA, danh sách sub-processor |
| Nhà cung cấp LLM (qua AI Gateway) | Trích xuất, giải thích | D7 (đã redact) | `VERIFY:` (vùng Bedrock; hoặc quốc gia của API ngoài) | Cần điều khoản không huấn luyện trên dữ liệu của ta |
| Nhà cung cấp OCR cloud (tùy chọn) | OCR baseline | Ảnh D1 | `VERIFY:` | Mặc định OCR cục bộ; chỉ dùng cloud sau khi có DPA + đánh giá |
| Nhà cung cấp email | Thông báo | Email, tên (D4) | `VERIFY:` | |
| IdP (Cognito/Keycloak) | Xác thực | D4 | `VERIFY:` | |

Kiểm soát chung: PHI Service là cổng duy nhất tới C4; vùng AI Worker không có internet; mọi gọi LLM qua AI Gateway có redact PII (SEC-AI-02) (plan §24).
