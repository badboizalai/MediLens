# Business Case — MediLens

Phiên bản 0.1 · 2026-10-23 · Owner: PO/PM · Task S1-T01 · Liên quan: [charter.md](charter.md)

## 1. Vấn đề
Bệnh nhân nhận bệnh án nhiều thuật ngữ, viết tắt, chữ tay, nhiều trang. Họ khó hình dung *tổn thương ở đâu, mức độ, ảnh hưởng cơ quan khác, thay đổi sau điều trị*. Bác sĩ ít thời gian giải thích. Kết quả: lo lắng, hiểu sai, hỏi lại nhiều lần. (Plan §2.1; số liệu thị trường chưa có, cần xác nhận qua nghiên cứu user ở S01–S02.)

## 2. Các phương án
| # | Phương án | Mô tả |
| --- | --- | --- |
| A | **Do nothing** | Không làm gì; bệnh nhân tiếp tục tự tra cứu (Google, nhóm mạng xã hội) |
| B | Chỉ OCR + glossary | Quét bệnh án, giải nghĩa thuật ngữ, không viewer |
| C | **MediLens đầy đủ (khuyến nghị)** | OCR + LLM extraction + review + viewer 2D/3D + timeline, giải thích có nguồn, 3 Unit MVP |
| D | Mua/tích hợp giải pháp có sẵn | Dùng sản phẩm tương tự hoặc app bệnh viện |

## 3. Chi phí và lợi ích
| Phương án | Chi phí | Lợi ích | Hạn chế / rủi ro |
| --- | --- | --- | --- |
| A | $0 | Không rủi ro pháp lý hay an toàn | Vấn đề giữ nguyên; không đạt G1–G5; không có sản phẩm portfolio |
| B | ~$10–30/tháng, ~400 giờ (ước tính thô) | Nhanh, rủi ro thấp | Không giải quyết "hình dung vị trí/diễn tiến"; giá trị khác biệt thấp |
| C | ~$20–80/tháng, ~1.000–1.200 giờ | Giải quyết đúng vấn đề; đạt đủ G1–G5; học quy trình enterprise; case study | Rủi ro an toàn, dữ liệu, pháp lý và quá tải (R01–R04, R07) cần kiểm soát |
| D | Phí giấy phép (chưa rõ) | Có sẵn | Chưa xác định sản phẩm phù hợp tiếng Việt và dữ liệu cá nhân; không đạt G5 (học) |

Lợi ích định lượng khi vận hành: trích xuất đúng vùng ≥ 85%, 100% giải thích có nguồn, activation/retention theo North Star (đặt ở OKR S02). Đây là dự án học tập và portfolio, nên **doanh thu chưa là mục tiêu v1.0**; chưa có mô hình thu phí.

## 4. Khuyến nghị
Chọn **phương án C**, giữ phạm vi minh họa/giải thích (BR-042) để tránh vào diện thiết bị y tế (Decree 98/2021; xác nhận bằng RDR tại G0-R). Điều kiện đi tiếp:
1. Có bác sĩ cố vấn trước S04 (R18).
2. Chỉ dữ liệu synthetic/public trước G3-P.
3. Quá tải thì cắt Unit hoặc timeline (Should), không cắt Hardening.
4. Điểm dừng: nếu G0/G0-R không đạt, quay về phương án B hoặc đóng dự án như case study.
