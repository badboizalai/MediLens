# Stakeholder Register và Governance — MediLens

Phiên bản 0.1 · 2026-10-23 · Owner: PO/PM · Task S1-T01 · Liên quan: [charter.md](charter.md), [business-case.md](business-case.md)

Tên người cụ thể để `<TBD>`; không ghi tên thật khi chưa được đồng ý.

## 1. Stakeholder register
Influence/Interest: H cao, M vừa, L thấp.

| Stakeholder | Vai trò | Mối quan tâm | Interest | Influence | Engagement |
| --- | --- | --- | --- | --- | --- |
| Project owner (learner) `<TBD>` | PO/PM, đóng mọi role | Giao v1.0, học quy trình | H | H | Quyết định hằng ngày; duyệt cổng |
| Mentor kỹ thuật `<TBD>` | Steering; review kiến trúc 1 lần/phase | Kiến trúc hợp lý, rủi ro kỹ thuật | M | H | Partner: họp cuối phase |
| Bác sĩ cố vấn `<TBD>` | Steering; ký G2-CS | An toàn bệnh nhân, nội dung y khoa đúng | H | H | Partner: review nội dung ~1 giờ/tháng, ký G2-CS |
| Bệnh nhân / người nhà (persona chính) | Người dùng cuối | Hiểu bệnh án, an tâm | H | M | Usability test 5–8 người, beta, feedback |
| Bác sĩ / người được chia sẻ | Người dùng phụ | Bản tóm tắt rõ, không bị thay vai | M | M | Phỏng vấn, tham vấn |
| Cơ quan quản lý (thiết bị y tế, dữ liệu cá nhân) | Pháp lý | Tuân thủ Decree 98/2021, Luật 91/2025, NĐ 356/2025 | L | H | Theo dõi; chỉ liên hệ khi G0-R/DPIA yêu cầu |
| Nhà cung cấp (LLM/OCR, cloud) | Vendor | Điều khoản, giá, vị trí xử lý dữ liệu | L | M | Đánh giá vendor; theo dõi deprecation |
| Nguồn dữ liệu/asset (dataset công khai, 3D) | Licensor | Tuân thủ license (NC/SA/DUA) | L | M | License Register trước khi tải |
| Tester usability, annotator (nếu có) | Hỗ trợ | Rõ nhiệm vụ, bảo mật | M | L | Thông tin định kỳ, NDA nếu cần |

## 2. Governance
**Steering committee:** Owner `<TBD>` (chủ trì, quyết định cuối) + Mentor `<TBD>` + Clinical advisor `<TBD>`. Clinical advisor có quyền chặn tại G2-CS; các role chặn khác (Regulatory, Security, QC) theo `docs/agents/project-context.md`.

**Quyết định:** Owner quyết định phạm vi/ưu tiên và ghi vào decision log. Thay đổi scope/ngân sách lớn: change request, Steering xem xét. Bất đồng giữa an toàn và tiến độ: an toàn thắng.

| Họp | Khi nào | Nội dung | Output |
| --- | --- | --- | --- |
| Steering cuối phase | Cuối P0 (G0, 2026-11-13), P1 (G1, 2026-12-25), P2 (G2), P3 (G3), P4 (G4), P5, P6 (G6) | Kết quả cổng, rủi ro đỏ, ngân sách, go/no-go | Biên bản, quyết định, hành động |
| Báo cáo tháng | Tuần đầu mỗi tháng, gửi Steering | Template §3 | Báo cáo (PR hoặc Notion) |
| Review/Retro sprint | Ngày cuối mỗi sprint (2 tuần) | Demo 5 phút, giữ/bỏ/thử, cập nhật risk | Cập nhật register |

**Escalation:** sự cố an toàn hoặc rò rỉ dữ liệu: báo ngay Owner và Clinical advisor; rò rỉ dữ liệu cá nhân báo cơ quan trong 72 giờ.

## 3. Template báo cáo tháng
```markdown
# Báo cáo tháng <YYYY-MM> — MediLens
Phase/Sprint: <...> · Tuần dự án: <n>/52 · Tình trạng: Xanh | Vàng | Đỏ

## 1. Tóm tắt (≤ 3 dòng)
## 2. Đã hoàn thành (sprint goal đạt / không)
## 3. Tiến độ vs kế hoạch (giờ công thực tế/kế hoạch; velocity)
## 4. Mục tiêu G1–G5: giá trị hiện tại vs ngưỡng
## 5. Rủi ro đỏ (≥ 15) và thay đổi điểm L×I
## 6. Ngân sách: chi tiền mặt tháng này / cap; % đã dùng
## 7. An toàn và tuân thủ: sự cố, finding mở, tiến độ cổng chặn
## 8. Quyết định cần Steering
## 9. Việc tháng tới
```
