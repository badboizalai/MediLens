# Claims control (UI, marketing, prompts, emails)

## Principle
Say what MediLens does: shows and explains what is already written in the user's own records. Never imply diagnosis, detection, prediction, treatment, certification or clinical proof without documented evidence.

## Forbidden or review-required phrasings
| Level | Vietnamese | English | Safer alternative |
| --- | --- | --- | --- |
| BLOCK | giúp chẩn đoán, tự chẩn đoán, AI chẩn đoán | diagnose(s) your…, AI diagnosis | "giúp bạn hiểu thông tin trong hồ sơ" / "helps you understand your records" |
| BLOCK | phát hiện bệnh, phát hiện ung thư, phát hiện sớm | detect(s) disease/cancer, early detection | "hiển thị các phát hiện đã ghi trong hồ sơ" / "shows findings written in your records" |
| BLOCK | thay thế bác sĩ, không cần đi khám | replaces your doctor, no need to see a doctor | "dùng cùng với lời khuyên của bác sĩ" / "use alongside your doctor's advice" |
| BLOCK | gợi ý điều trị, liều dùng, nên uống thuốc | treatment recommendation, dosage, you should take | remove; route to clinician |
| BLOCK | tiên lượng, dự đoán thời gian sống | prognosis, survival prediction | remove |
| BLOCK | chính xác 100%, đã được Bộ Y tế cấp phép (khi không đúng) | 100% accurate, approved/certified (when not true) | state measured accuracy with scope, or nothing |
| REVIEW | chẩn đoán (bare) | diagnosis (bare) | OK only when quoting the record's own field, e.g. "Chẩn đoán (theo hồ sơ)" |
| REVIEW | an toàn tuyệt đối, bảo mật tuyệt đối | completely secure | "được mã hóa và kiểm soát truy cập" / "encrypted and access-controlled" |
| REVIEW | được bác sĩ kiểm chứng | clinically validated/proven | only with a VAL report reference and its scope |

## Process
1. Writer/UX/AI owner runs `scripts/claims_lint.py` on changed files (also in CI for i18n and prompt folders).
2. Regulatory reviews BLOCK and REVIEW findings; legitimate record quotes are annotated with `claims-ok` on the same line (JSON: add the key to an allowlist file).
3. Decision recorded in `assets/claims-review-record.md`.
