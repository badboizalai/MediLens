# Forbidden claims — MediLens (VI/EN)

> **Draft — educational, not legal advice; requires human REG sign-off at G0-R.**
> Nguồn: `claims-control.md` và `scripts/claims_lint.py` của skill medilens-regulatory-privacy-officer; BR-042; `docs/plan/project-plan.vi.md` §22.2 mục 4. Phạm vi áp dụng: UI, i18n, prompt LLM, landing page, store listing, email, tài liệu hỗ trợ.

Nguyên tắc: nói MediLens **làm gì** (hiển thị và giải thích điều đã có trong hồ sơ của chính người dùng), không ngụ ý chẩn đoán, phát hiện, dự đoán, điều trị, chứng nhận hay bằng chứng lâm sàng khi chưa có tài liệu.

Cách dùng với linter: `python3 .claude/skills/medilens-regulatory-privacy-officer/scripts/claims_lint.py <file|folder>`. Tệp này tự liệt kê cụm cấm nên mỗi dòng đều gắn `claims-ok`; **không** copy các cụm này vào nội dung sản phẩm. Khi trích đúng tên trường của hồ sơ (ví dụ "Chẩn đoán (theo hồ sơ)") hãy gắn `claims-ok` cùng dòng.

## BLOCK — cấm tuyệt đối

| Mức | Tiếng Việt (cấm) | English (forbidden) | Thay bằng / Allowed alternative |
| --- | --- | --- | --- |
| BLOCK | giúp chẩn đoán, tự chẩn đoán, AI chẩn đoán, ứng dụng chẩn đoán | diagnoses your…, helps diagnose, AI diagnosis, automated diagnosis | "giúp bạn hiểu thông tin trong hồ sơ" / "helps you understand your records" | <!-- claims-ok -->
| BLOCK | phát hiện bệnh, phát hiện ung thư, phát hiện khối u/tổn thương, phát hiện sớm | detects disease/cancer/tumours/lesions, early detection | "hiển thị các phát hiện đã ghi trong hồ sơ" / "shows findings written in your records" | <!-- claims-ok -->
| BLOCK | thay thế bác sĩ, không cần đi khám | replaces your doctor, no need to see a doctor | "dùng cùng với lời khuyên của bác sĩ" / "use alongside your doctor's advice" | <!-- claims-ok -->
| BLOCK | gợi ý/đề xuất/khuyến nghị điều trị, phác đồ điều trị | treatment recommendation(s) | Bỏ; chuyển về bác sĩ / Remove; refer to a clinician | <!-- claims-ok -->
| BLOCK | liều dùng, liều lượng, nên uống/dùng/ngừng thuốc | dosage, dosing, you should take / stop taking | Bỏ; "hỏi bác sĩ hoặc dược sĩ" / Remove; "ask your doctor or pharmacist" | <!-- claims-ok -->
| BLOCK | tiên lượng, dự đoán/ước tính thời gian sống | prognosis, prognostic, survival rate/time/prediction | Bỏ hoàn toàn / Remove entirely (BR-022/023) | <!-- claims-ok -->
| BLOCK | chính xác 100% | 100% accurate | Nêu độ chính xác đo được kèm phạm vi, hoặc không nêu / State measured accuracy with scope, or nothing | <!-- claims-ok -->
| BLOCK | được Bộ Y tế cấp phép / chứng nhận / phê duyệt (khi không đúng) | FDA/CE/Ministry of Health approved / cleared / certified (when not true) | Chỉ nêu khi đúng và có hồ sơ / Only if true and documented | <!-- claims-ok -->

## BLOCK bổ sung theo BR-042 (chưa có trong linter — kiểm tay)

| Mức | Tiếng Việt (cấm) | English (forbidden) | Thay bằng |
| --- | --- | --- | --- |
| BLOCK | AI đọc phim, AI tìm tổn thương trên CT, đo kích thước khối u tự động | AI reads your scan, automatic tumour measurement, finds lesions on CT | "dựng hình minh họa giải phẫu từ CT" / "builds an illustrative anatomy model from CT" | <!-- claims-ok -->
| BLOCK | cảnh báo bệnh nặng thêm, điểm nguy cơ, nguy cơ mắc bệnh X% | risk score, your risk of disease is X% | Bỏ / Remove | <!-- claims-ok -->
| BLOCK | triệu chứng này có thể là bệnh… | your symptoms may mean… (symptom checker) | Bỏ; "nên trao đổi với bác sĩ" / Remove; "discuss with your doctor" | <!-- claims-ok -->
| BLOCK | cảnh báo chỉ số xấu đi, xu hướng nguy hiểm | alerts you when your results get worse | "hiển thị giá trị đã ghi và khoảng tham chiếu của phòng xét nghiệm" / "shows recorded values and the lab's printed reference range" | <!-- claims-ok -->
| BLOCK | màu đỏ nghĩa là nguy hiểm/nghiêm trọng (khi tự suy luận) | red means dangerous (when inferred by us) | Màu chỉ theo mức ghi trong hồ sơ, có chú giải / Colour only by level recorded in the record, with legend | <!-- claims-ok -->

## REVIEW — cần Regulatory/CSO duyệt trước khi dùng

| Mức | Tiếng Việt | English | Điều kiện / Safer alternative |
| --- | --- | --- | --- |
| REVIEW | "chẩn đoán" đứng riêng | "diagnosis" on its own | Chỉ khi trích đúng trường của hồ sơ: "Chẩn đoán (theo hồ sơ)" kèm `claims-ok` | <!-- claims-ok -->
| REVIEW | an toàn tuyệt đối, bảo mật tuyệt đối | completely secure, 100% secure | "được mã hóa và kiểm soát truy cập" / "encrypted and access-controlled" | <!-- claims-ok -->
| REVIEW | được bác sĩ kiểm chứng | clinically validated / clinically proven | Chỉ khi có báo cáo VAL và nêu phạm vi / Only with a VAL report and its scope | <!-- claims-ok -->
| REVIEW | an toàn cho bệnh nhân, đạt chuẩn y tế, đạt ISO 13485/14971 | patient-safe, medical-grade, ISO-certified | Không có chứng nhận thì không nói; có thể nói "áp dụng tinh thần ISO 14971" / If not certified, do not say; may say "follows ISO 14971 principles" | <!-- claims-ok -->

## Ghi chú

- Danh sách cấm này là kiểm soát bổ trợ; ranh giới thật nằm ở thiết kế sản phẩm (BR-042) và ở RDR-001.
- Cập nhật danh sách qua PR; mỗi thay đổi phải ghi vào `claims-review-record.md` của skill. Rà soát lại cùng ngày với RDR-001 (xem RDR-001 mục Ngày rà soát).
- `VERIFY:` linter hiện không bắt các cụm ở bảng "BR-042 bổ sung"; đề xuất bổ sung quy tắc vào `claims_lint.py` bằng một task riêng (ngoài phạm vi S1-T02).
