# Intended Use Statement — MediLens v1

> **Trạng thái: Draft — educational, not legal advice; requires human REG sign-off at G0-R.**
> Nguồn: `intended-use-statement-template.md` (skill regulatory-privacy-officer), `docs/plan/project-plan.vi.md` §22.2. Quyết định pháp lý đi kèm: [RDR-001](RDR-001.md). Danh sách cụm từ cấm: [forbidden-claims.md](forbidden-claims.md).

## Mục đích sử dụng (Intended purpose)

MediLens giúp người dùng xem lại và hiểu thông tin **đã được ghi sẵn** trong hồ sơ y tế của chính họ, bằng cách hiển thị các mục trong hồ sơ trên mô hình cơ thể minh họa 2D/3D (tô màu theo `region_code`) và cung cấp nội dung giải thích mang tính giáo dục, có nguồn trích dẫn.

*EN: MediLens helps people review and understand information already written in their own health records, by showing the recorded items on illustrative body models and providing sourced educational explanations.*

## Người dùng dự kiến (Intended users)

- Người trưởng thành tự quản lý hồ sơ của mình.
- Người chăm sóc quản lý hồ sơ của người phụ thuộc (hồ sơ trẻ em chỉ do người giám hộ tạo, BR-001).
- Bác sĩ xem hồ sơ được người dùng chia sẻ (chỉ xem).

## Đầu vào (Inputs)

- Ảnh chụp hoặc PDF scan của hồ sơ; bệnh án số (PDF có lớp chữ, DOCX, FHIR) (BR-045).
- Văn bản người dùng tự mô tả, luôn gắn nhãn "người dùng tự khai" (BR-040).
- (v2, chưa thuộc phạm vi v1) Chuỗi CT chỉ dùng để dựng giải phẫu minh họa (BR-042) — cần chạy lại G0-R trước khi làm.

## Đầu ra (Outputs)

- Các mục thông tin đã được **người dùng xác nhận** ở màn hình review.
- Hình minh họa 2D/3D, dòng thời gian các lần khám.
- Nội dung giải thích giáo dục có trích dẫn nguồn, được CSO duyệt.

## Ngoài phạm vi — MediLens KHÔNG làm (BR-042)

| # | Không làm | Ghi chú |
| --- | --- | --- |
| 1 | Không đưa ra kết luận về bệnh (không có chẩn đoán, không có danh sách bệnh nghi ngờ) | Chỉ hiển thị nội dung hồ sơ đã ghi; trường "Chẩn đoán (theo hồ sơ)" là trích nguyên văn | <!-- claims-ok -->
| 2 | Không đề xuất, thay đổi hay ngừng điều trị/thuốc; không đưa liều | Mọi câu hỏi về điều trị chuyển về bác sĩ |
| 3 | Không phân tích hình ảnh để phát hiện, đo hay mô tả đặc điểm tổn thương | Áp dụng cho ảnh chụp, X-quang, CT, ảnh da, răng; CT chỉ dựng hình minh họa |
| 4 | Không dự đoán diễn tiến, thời gian sống, không chấm điểm nguy cơ | BR-022/023 |
| 5 | Không phân loại mức khẩn cấp; mọi tình huống cấp cứu luôn hướng đến số **115** | Duy nhất ngoại lệ là chuyển hướng cấp cứu |
| 6 | Không thay thế bác sĩ hay cơ sở y tế | Luôn khuyến khích dùng cùng lời khuyên của bác sĩ | <!-- claims-ok -->
| 7 | Không cảnh báo diễn biến chỉ số theo dõi (xu hướng xấu đi) | Chỉ hiển thị giá trị đã ghi và khoảng tham chiếu in trong hồ sơ |

Bản tiếng Anh (dùng trong About page / store listing): *MediLens does not make a diagnosis [claims-ok], does not recommend treatment or medication, does not analyse images to detect or measure disease, does not predict outcomes, and does not replace a clinician. In an emergency, call 115.* <!-- claims-ok -->

## Môi trường sử dụng

Trình duyệt web trên thiết bị cá nhân. Không dùng trong cấp cứu. Nội dung này hiển thị ở trang About của ứng dụng.

## Điều kiện duy trì ranh giới

Tính năng mới thuộc nhóm "gần thiết bị y tế" (tự phát hiện/đo tổn thương, điểm nguy cơ, gợi ý điều trị, cảnh báo xu hướng chỉ số, hỗ trợ quyết định cho bác sĩ) phải có RDR mới trước khi xây (xem RDR-001, mục kích hoạt đánh giá lại). <!-- claims-ok -->

## Kiểm soát phiên bản

| Phiên bản | Ngày | Người soạn | Duyệt (Regulatory) | Rà soát (CSO) |
| --- | --- | --- | --- | --- |
| 0.1-draft | 2026-10-23 | Claude (vai Regulatory officer, S1-T02) | **Chờ — cần người thật ký tại G0-R** | **Chờ** |
