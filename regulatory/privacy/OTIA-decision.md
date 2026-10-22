# OTIA decision (đánh giá tác động chuyển dữ liệu ra nước ngoài)

> **Draft — educational, not legal advice; requires human DPO/REG sign-off.**
> Người soạn là một agent AI. Mọi chi tiết pháp lý chưa chắc chắn được đánh dấu `VERIFY:`.

| Field | Value |
| --- | --- |
| Quyết định | **Required (bắt buộc).** Hồ sơ OTIA (Form 09 theo NĐ 356/2025, `VERIFY:` số mẫu) phải **nộp trong vòng 60 ngày kể từ khi bắt đầu xử lý dữ liệu thật**, và cập nhật khi đổi nhà nhận/mục đích. |
| Ngày | 2026-10-23 |
| Tình trạng hiện tại | Chưa xử lý dữ liệu thật (dev/staging dùng dữ liệu tổng hợp) nên chưa bắt đầu đếm 60 ngày. Ghi ngày bắt đầu xử lý dữ liệu thật: `____`. Hạn nộp = ngày đó + 60 ngày. |
| Người ký | DPO + REG (người thật) |

## Lý do

Điều kiện kích hoạt: có xử lý hoặc lưu trữ dữ liệu cá nhân ngoài Việt Nam. MediLens thỏa điều kiện vì:

1. Hạ tầng chính ở **AWS ap-southeast-1 (Singapore)**: lưu D1-D12 trong data-inventory.md.
2. Gọi **LLM** qua AI Gateway, có thể ở vùng/quốc gia khác Việt Nam (`VERIFY:` vùng Bedrock, cross-region inference).
3. Có thể dùng nhà cung cấp OCR cloud và email ngoài nước.

`VERIFY:` định nghĩa "chuyển dữ liệu ra nước ngoài" trong Luật 91/2025/QH15 / NĐ 356/2025: lưu trữ trên máy chủ nước ngoài có được coi là chuyển hay không, và dữ liệu đã redact/giả danh có được loại trừ không. Cho đến khi xác nhận, giả định là **có** (cách thận trọng).

## Nội dung hồ sơ OTIA phải có

- [ ] Bên chuyển (controller) và bên nhận ở nước ngoài: AWS (Singapore); nhà cung cấp LLM, OCR, email (pháp nhân, quốc gia, liên hệ).
- [ ] Mục đích chuyển, tách riêng từng mục đích (lưu trữ/xử lý, trích xuất, giải thích, email).
- [ ] Loại dữ liệu và khối lượng ước tính (theo data-inventory.md), nêu rõ dữ liệu nhạy cảm (sức khỏe) và dữ liệu trẻ em.
- [ ] Biện pháp bảo vệ: mã hóa KMS CMK, mã hóa trường, redact PII trước LLM, vùng AI không internet, kiểm soát truy cập/kiểm toán, DPA với từng nhà nhận, điều khoản **không huấn luyện trên dữ liệu của MediLens**, danh sách sub-processor, điều khoản xóa dữ liệu.
- [ ] Đánh giá rủi ro cho chủ thể dữ liệu và biện pháp giảm thiểu (liên kết DPIA-v0.md).
- [ ] Bằng chứng consent bao gồm xử lý ở nước ngoài (văn bản consent và thông báo quyền riêng tư nêu rõ).
- [ ] Rà soát pháp luật nước nhận (Singapore và nước của nhà cung cấp LLM) về khả năng truy cập của chính quyền `VERIFY:`.
- [ ] Cách chủ thể thực hiện quyền khi dữ liệu ở nước ngoài; quy trình DSR.
- [ ] Kế hoạch ứng phó sự cố/vi phạm (72 giờ) áp dụng cho bên nhận.
- [ ] Bằng chứng nộp (ngày, người nộp, số tiếp nhận) và lịch cập nhật khi đổi nhà nhận.

## Hành động trước khi dùng dữ liệu thật

1. Chốt nhà cung cấp LLM/OCR/email và vùng; cập nhật data-inventory.md.
2. Ký DPA, có điều khoản không huấn luyện.
3. Hoàn tất DPIA (DPIA-v0.md lên v1) và OTIA; đặt nhắc việc trước hạn 60 ngày.
4. Người thật (DPO/REG) rà soát và ký; `VERIFY:` với luật sư về thủ tục nộp, cơ quan tiếp nhận, mẫu hiện hành.
