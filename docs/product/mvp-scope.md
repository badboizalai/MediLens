# MVP Scope — MoSCoW

Phiên bản 0.1 · 2026-10-23 · Owner: BA (`medilens-business-analyst`), reviewer: PO/PM · Task S2-T07 · Liên quan: [charter](../project/charter.md) §3, [problem-statement.md](problem-statement.md) · Nguồn: plan §2.4, §3.1 · Khóa chính thức tại G0 (2026-11-13)

## 1. Nguyên tắc
MVP (v1.0) khóa ở **3 Unit: Răng hàm mặt (Dental), Nội tim mạch (Cardiology), Ung bướu (Oncology)**. Kiến trúc cho phép thêm Unit chỉ bằng config + asset (plan §3), nhưng v1.0 không thêm. Giảm rủi ro R03 (một người ôm quá nhiều).

## 2. Bảng MoSCoW
| Tính năng | v1.0 (MVP) | v1.5 | v2.0 |
| --- | --- | --- | --- |
| Auth (email, Google OAuth), MFA | Must | | |
| Upload ảnh/PDF, OCR tiếng Việt + Anh | Must | | |
| Trích xuất chẩn đoán, vị trí, mức độ, ngày | Must | | |
| Màn hình review/sửa của người dùng | Must | | |
| Viewer 2D + 3D toàn thân | Must | | |
| 3 Unit: Dental, Cardiology, Oncology (**tối đa 3**) | Must | | |
| Giải thích LLM + RAG có trích dẫn, disclaimer | Must | | |
| Timeline pre/post | Should | | |
| Chia sẻ với bác sĩ/người thân (có hạn) | Should | | |
| Unit thêm: Surgery, Nephrology-Urology, Gastroenterology, Respiratory | | Could | |
| Computer vision trên ảnh tổn thương (da, răng) | | Could | |
| Nhắc lịch và thông báo | | Could | |
| DICOM/CT (cần chạy lại G0-R) | | | Could |
| Unit thêm: Dermatology, Ophthalmology, ENT | | | Could |

Ghi chú: Should ở v1.0 vẫn nằm trong phạm vi v1.0 của charter §3, nhưng bị cắt trước Must khi trễ. Số Unit Must là 3, không vượt.

## 3. Điều kiện chấp nhận
- Số Unit "Must" ≤ 3 (đếm dòng Unit trong bảng §2).
- Mọi mục Must có acceptance criteria trong BRD/SRS trước G0.

## 4. Won't (ngoài phạm vi, v1.0 và v1.5)
- Chẩn đoán, gợi ý điều trị, kê đơn/liều, tiên lượng (BR-042).
- Kết nối HIS/EMR của bệnh viện; FHIR export/import (không làm ở v1).
- App di động native (web responsive thì có).
- Thanh toán, bảo hiểm.
- Dữ liệu bệnh nhân thật trước G3-P.
- Tự động phát hiện/đo tổn thương trên ảnh CT (BR-042).

## 5. Chặn scope creep: yêu cầu Unit mới
1. Mọi yêu cầu thêm Unit hoặc tính năng Must mới là **change request**, không nhận qua chat/PR trực tiếp.
2. BA ghi CR: lý do, giá trị, giả thuyết liên quan, tác động công/rủi ro/an toàn/pháp lý (hỏi `medilens-clinical-safety-officer` và `medilens-regulatory-privacy-officer` nếu chạm nội dung y khoa hoặc intended use).
3. PO/PM quyết định, ghi vào decision log. Mặc định: **đưa vào v1.5**.
4. Chỉ vào v1.0 nếu hoán đổi: bỏ một Unit hoặc Must khác cùng công sức, để Unit Must vẫn ≤ 3.
5. Sau G0, thay đổi Must cần PO/PM ký và cập nhật charter + tài liệu này (tăng phiên bản).
