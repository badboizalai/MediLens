# Project Charter — MediLens

Phiên bản 0.1 · 2026-10-23 · Owner: PO/PM (`medilens-product-manager`) · Task S1-T01 · Trạng thái: Draft chờ G0

## 1. Mục đích
MediLens là web app giúp bệnh nhân **hiểu bệnh án của chính mình**: upload (ảnh/PDF/digital/text) → OCR + LLM extraction → người dùng review → viewer 2D/3D tô màu theo vùng cơ thể. App **minh họa và giải thích, không chẩn đoán, không kê liều, không tiên lượng** (BR-042). Lý do kinh doanh: xem [business-case.md](business-case.md). Các bên liên quan và governance: [stakeholders.md](stakeholders.md).

## 2. Mục tiêu đo được
| # | Mục tiêu | Thước đo |
| --- | --- | --- |
| G1 | Upload bệnh án và thấy tổn thương trên mô hình cơ thể | ≥ 85% tài liệu test được trích xuất và gắn đúng `region_code` |
| G2 | Giải thích dễ hiểu, có nguồn, không thay bác sĩ | 100% câu trả lời AI có trích dẫn + disclaimer |
| G3 | Theo dõi diễn tiến theo thời gian | Timeline ≥ 2 mốc cho cùng một tổn thương |
| G4 | Chuẩn "enterprise" | CI/CD, coverage ≥ 70%, SLO 99.5%, audit log đầy đủ |
| G5 | Học quy trình dự án lớn | Đủ bộ tài liệu (BRD, SRS, ADR, runbook...) |

## 3. Phạm vi
- **Trong (v1.0):** auth và hồ sơ, upload + OCR, trích xuất thực thể y khoa, mapping vùng giải phẫu, viewer 3D/2D cho 3 Unit (Răng hàm mặt, Tim mạch, Ung bướu), timeline pre/post, giải thích LLM + RAG có trích dẫn, chia sẻ có hạn, admin và audit.
- **Ngoài:** chẩn đoán, kê đơn, kết nối HIS/EMR, DICOM/CT chuyên sâu (v2.0, cần chạy lại G0-R), thanh toán bảo hiểm, dữ liệu bệnh nhân thật trước G3-P.

## 4. Ngân sách
- **Công:** ~1.000–1.200 giờ (20 giờ/tuần, part-time, một người đảm nhận mọi role).
- **Tiền mặt (plan §12.2), ước tính, cần kiểm tra lại giá thực tế:**

| Hạng mục | $/tháng |
| --- | --- |
| GPU (Colab/Kaggle, thuê theo giờ) | 0–20 |
| Hosting (VPS 4 vCPU/8 GB) | 10–25 |
| Cloud học enterprise (free tier/credit) | 0–50 |
| LLM API (có cache, budget cap) | 5–30 |
| Domain + email | 1–5 |
| Công cụ (gói miễn phí) | 0 |

Mục tiêu tổng: **~$20–80/tháng**; cảnh báo ở 80% ngân sách (R12). Dự phòng: buffer 20% thời gian.

## 5. Tiêu chí thành công
1. Đạt G1–G5 ở bảng §2 tại G4 (launch v1.0).
2. Tất cả cổng chặn (G0-R, G1-D, G2-CS, G3, G3-P) đạt, có chữ ký role phụ trách; G2-CS cần bác sĩ cố vấn thật ký.
3. Không có dữ liệu bệnh nhân thật trước G3-P; không vi phạm BR-042.
4. Chi phí tiền mặt ≤ ngân sách §4; v1.0 ra mắt đúng tuần 32 (±1 sprint).

## 6. Top-5 rủi ro (L × I; ≥ 15 là đỏ)
| ID | Rủi ro | L | I | Điểm | Giảm thiểu chính |
| --- | --- | --- | --- | --- | --- |
| R03 | Một người ôm quá nhiều, kiệt sức, bỏ dở | 4 | 4 | 16 | MVP 3 Unit, timebox, buffer 20%, cho phép cắt scope |
| R04 | LLM bịa thông tin (hallucination) | 4 | 4 | 16 | Structured output + citation, human review, RAG nguồn đã duyệt |
| R01 | Hiểu nhầm minh họa là chẩn đoán | 3 | 5 | 15 | Disclaimer mọi màn, không tiên lượng, guardrail |
| R02 | Rò rỉ dữ liệu sức khỏe | 3 | 5 | 15 | Threat model, authz test, RLS, mã hóa, chỉ synthetic |
| R07 | Vi phạm Luật 91/2025 / NĐ 356/2025 | 3 | 5 | 15 | Consent, DPIA, redaction, OTIA trong 60 ngày |

Danh sách đầy đủ: plan §11 và `risk-register.md` của PM skill. R18 (chưa có bác sĩ cố vấn, 3×4=12) cần đóng trong S01–S04.

## 7. Mốc và cổng
S01 bắt đầu 2026-10-19; sprint 2 tuần; ngày = thứ Sáu cuối sprint.

| Cổng | Sprint | Ngày | Nội dung |
| --- | --- | --- | --- |
| G0, G0-R | S02 | 2026-11-13 | Khóa scope MVP, BRD, prototype, Intended Use, RDR |
| G1, G1-D | S05 | 2026-12-25 | ADR chốt, CI xanh, 1 tài liệu chạy end-to-end trên staging; License Register |
| G2 | S11 | 2027-03-19 | Feature complete |
| G2-CS | S13 | 2027-04-16 | Clinical Safety Case ký |
| G3, G3-P | S14 | 2027-04-30 | Release gate, pentest độc lập |
| G4 | S16 | 2027-05-28 | **Launch v1.0 (tuần 32)** |
| G5-H / G5 / G6 | S18 / S20 / S26 | 2027-06-25 / 07-23 / 10-15 | Hypercare exit / v1.5 / v2.0 CT |

Nguồn: `docs/plan/MediLens_Sprint_Plan_52w.xlsx` (số sprint của từng cổng); ngày tính từ ngày bắt đầu S01. Nếu sheet lệch, sheet là chuẩn.

## 8. Giả định và ràng buộc
Dữ liệu synthetic/public có license; stack và kiến trúc theo `docs/agents/project-context.md`; mọi thay đổi scope qua change request và decision log.
