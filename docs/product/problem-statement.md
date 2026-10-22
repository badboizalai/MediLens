# Problem Statement — MediLens

Phiên bản 0.1 · 2026-10-23 · Owner: BA (`medilens-business-analyst`), reviewer: PO/PM · Task S2-T07 · Liên quan: [charter](../project/charter.md), [business case](../project/business-case.md), [mvp-scope.md](mvp-scope.md)

> Toàn bộ "bằng chứng" dưới đây là **giả thuyết** cho đến khi hoàn tất phỏng vấn 5–8 người (plan §2.5). Không có số liệu thị trường nào được trích dẫn.

## 1. Ai gặp vấn đề
| Nhóm | Mô tả | Nhu cầu chính |
| --- | --- | --- |
| Bệnh nhân (chính) | 25–65 tuổi, dùng smartphone, không có nền y khoa | Hiểu bệnh của mình, theo dõi diễn tiến |
| Người chăm sóc | Con/cha mẹ chăm một bệnh nhân | Xem hồ sơ người thân khi được phép |
| Bác sĩ nhận chia sẻ (phụ) | Bác sĩ được bệnh nhân chia sẻ | Tóm tắt nhanh, sửa trích xuất sai |

Nguồn: plan §2.2.

## 2. Nỗi đau
Bệnh án chứa thuật ngữ, viết tắt, chữ tay, nhiều trang. Bệnh nhân không hình dung được *tổn thương ở đâu, mức độ ra sao, ảnh hưởng cơ quan khác thế nào, thay đổi gì sau điều trị*. Bác sĩ ít thời gian giải thích. Hệ quả giả định: lo lắng, hiểu sai, hỏi lại nhiều lần, thất lạc giấy tờ.

## 3. Bằng chứng (giả thuyết, chưa kiểm chứng)
| # | Giả thuyết | Cách kiểm chứng | Trạng thái |
| --- | --- | --- | --- |
| H1 | Bệnh nhân khó hiểu thuật ngữ/vị trí tổn thương trong bệnh án | Phỏng vấn 5–8 người từng nằm viện | Chưa kiểm chứng |
| H2 | Hình minh họa theo vùng cơ thể giúp hiểu hơn văn bản | Usability test trên prototype | Chưa kiểm chứng |
| H3 | Người dùng sẵn sàng tải bệnh án lên nếu consent rõ ràng | Phỏng vấn + hỏi về lo ngại dữ liệu | Chưa kiểm chứng |
| H4 | Bệnh nhân Răng hàm mặt, Tim mạch, Ung bướu có nhu cầu hình dung rõ nhất | Phỏng vấn, đối chiếu mẫu bệnh án | Chưa kiểm chứng |
| H5 | Giải pháp hiện tại (Google, nhóm mạng xã hội) không đủ tin cậy | Khảo sát đối thủ (BioDigital, Ada, PHR Việt Nam) | Chưa kiểm chứng |

Kết quả phỏng vấn sẽ cập nhật bảng này; giả thuyết bị bác bỏ phải đi qua change request (xem mvp-scope.md §5).

## 4. Tuyên bố vấn đề
Bệnh nhân và người chăm sóc nhận bệnh án khó hiểu và không hình dung được tình trạng của mình, trong khi bác sĩ không có thời gian giải thích. MediLens biến bệnh án thành hình minh họa theo vùng cơ thể kèm giải thích có trích nguồn, để người dùng **hiểu** hồ sơ của mình và hỏi bác sĩ tốt hơn.

## 5. Ranh giới
MediLens minh họa và giải thích; **không chẩn đoán, không kê liều, không tiên lượng** (BR-042). Mọi nội dung AI gắn nhãn, có nguồn và disclaimer. Danh sách "Won't" ở [mvp-scope.md](mvp-scope.md) §4.
