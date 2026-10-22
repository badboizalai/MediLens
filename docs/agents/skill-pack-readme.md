# MediLens Agent Skills — bộ kỹ năng theo từng role / role-based skill pack

> Tiếng Việt ở trên, English below.

## 1. Đây là gì?
Bộ **23 skill** (phiên bản 1.1: thêm 9 role ở Phần III của kế hoạch) theo chuẩn Agent Skills của Anthropic (mỗi skill là một thư mục có `SKILL.md` với YAML frontmatter `name` + `description`, kèm `references/`, `assets/`, `scripts/`). Mỗi skill đại diện cho một **role** trong dự án MediLens. Khi bạn đưa một vấn đề cho Claude, Claude đọc phần `description` của các skill và tự nạp skill phù hợp; skill **`medilens-orchestrator`** đóng vai trò điều phối: phân loại vấn đề → chọn role chính và role review → viết task brief → chuyển giao (hand-off) có cổng kiểm tra.

| Skill | Role | Dùng khi |
| --- | --- | --- |
| `medilens-orchestrator` | Điều phối / delivery lead | Không rõ ai phụ trách, việc liên quan nhiều role, cần kế hoạch end-to-end |
| `medilens-business-analyst` | BA | Yêu cầu, user story, Gherkin, business rule, glossary, UAT |
| `medilens-product-manager` | PO / PM | Ưu tiên, sprint, roadmap, OKR, rủi ro, go/no-go |
| `medilens-ux-ui-designer` | UX/UI | Màn hình, luồng, viewer, câu chữ, token, accessibility |
| `medilens-solution-architect` | Solution Architect | ADR, NFR, chọn công nghệ, mẫu tích hợp, C4 |
| `medilens-ai-ml-engineer` | AI Solution / ML | OCR, CV, LLM extraction, mapping, RAG, guardrail, eval |
| `medilens-data-engineer` | Data Engineer | Phân loại dữ liệu, pipeline, dbt, DQ, contract, retention, xóa dữ liệu |
| `medilens-backend-engineer` | Backend | API FastAPI, phân quyền, migration, worker, outbox, test |
| `medilens-frontend-engineer` | Frontend | Next.js, viewer 3D/2D, Unit plugin, asset GLB/SVG, hiệu năng |
| `medilens-cloud-devops-engineer` | Cloud / DevOps | Chọn dịch vụ AWS, Terraform, CI/CD, deploy, chi phí |
| `medilens-security-engineer` | Security & Compliance | Threat model, review, OWASP, Luật BVDLCN 91/2025 + NĐ 356/2025, kiến trúc PHI (SEC-AR), pentest G3-P, sự cố |
| `medilens-qa-engineer` | QA | Chiến lược test, test case, automation, k6, AI gate |
| `medilens-qc-release-gatekeeper` | QC | Cổng phát hành, exploratory, duyệt nội dung y khoa, UAT |
| `medilens-sre-operations` | SRE / Maintain | SLO, alarm, sự cố, runbook, DR, lịch bảo trì |
| `medilens-clinical-safety-officer` ★ | Clinical Safety Officer (bác sĩ cố vấn) | Hazard log, Clinical Safety Case (G2-CS), duyệt hiển thị/nội dung y khoa, xác thực lâm sàng, phản hồi an toàn sau ra mắt |
| `medilens-regulatory-privacy-officer` ★ | Regulatory, Privacy & Legal (DPO) | Intended use, có phải thiết bị y tế không (RDR, G0-R), DPIA/OTIA, consent, kiểm soát tuyên bố, hợp đồng, đánh giá tác động AI |
| `medilens-clinical-informaticist` | Clinical Informaticist | ICD-10/LOINC/SNOMED/FDI/UCUM, cây vùng giải phẫu, FHIR, nhập bệnh án số |
| `medilens-data-curator` ★ | Data Curator & Annotation Lead | Nguồn dữ liệu, license (G1-D), gán nhãn, kappa, cỡ mẫu, version dataset, dữ liệu đóng góp |
| `medilens-mlops-engineer` | MLOps (+ FinOps token) | AI Gateway, cascade model, chi phí token/GPU, registry, shadow/canary, distillation |
| `medilens-medical-imaging-engineer` | Medical Imaging | DICOM/CT, khử định danh, segmentation, mesh, registration, viewer lát cắt |
| `medilens-3d-medical-artist` | 3D Medical Artist | GLB/SVG giải phẫu, đặt tên region_code, ngân sách, thư viện template, glyph thiết bị |
| `medilens-technical-writer` | Technical Writer & Localization | Hướng dẫn, FAQ, release notes, dịch VI↔EN, kiểm tra i18n |
| `medilens-support-success` | Support & Customer Success | Mô hình hỗ trợ, ticket, macro, hypercare (G5-H), knowledge base |

★ = bạn vẫn đóng vai để học, nhưng cần người thật có chuyên môn ký trước khi dùng dữ liệu thật hoặc ra mắt công khai.

## 2. Cách agent làm việc với skill
1. Bạn mô tả vấn đề (ví dụ: "OCR đọc sai số răng trong ảnh chụp mờ").
2. Claude khớp `description` → nạp `medilens-ai-ml-engineer` (hoặc orchestrator nếu vấn đề chạm nhiều role).
3. Skill yêu cầu đọc `references/project-context.md` (ngữ cảnh chung), chọn **workflow** phù hợp trong bảng "Workflow selector", đọc thêm reference cần thiết, dùng template trong `assets/` và chạy script trong `scripts/`.
4. Kết quả có cấu trúc + checklist chất lượng; nếu cần role khác, skill ghi rõ hand-off (ví dụ chuyển cho `medilens-security-engineer` review).
5. Gọi trực tiếp (Claude Code): gõ `/medilens-backend-engineer <yêu cầu>`.

## 3. Cài đặt
- **Claude Code (máy cá nhân):** chép từng thư mục skill vào `~/.claude/skills/` (dùng cho mọi project) hoặc `.claude/skills/` trong repo MediLens (chia sẻ qua git).
- **claude.ai / Claude app:** tải lên từng file zip trong `dist/` ở phần Skills của cài đặt (mỗi zip là một skill).
- **Claude API (Skills API):** tải lên từng skill dạng zip theo tài liệu Agent Skills.
Các skill chỉ dùng trường frontmatter tương thích mọi nền tảng: `name`, `description`, `license`, `compatibility`, `metadata`.

## 4. Cấu trúc một skill
```
medilens-<role>/
├── SKILL.md            # frontmatter + quy trình làm việc (workflow selector W1…Wn)
├── references/         # kiến thức chi tiết, nạp khi cần (project-context.md có ở mọi skill)
├── assets/             # template tài liệu, code mẫu, cấu hình
└── scripts/            # công cụ chạy được (Python, chỉ thư viện chuẩn trừ khi ghi chú)
```

## 5. Script có sẵn
| Script | Skill | Chức năng |
| --- | --- | --- |
| `check_traceability.py` | BA | BR → story → test còn thiếu |
| `rice_score.py` | PM | Chấm điểm RICE và xếp hạng backlog |
| `eval_extraction.py` | AI/ML | P/R/F1 theo trường, theo Unit, CER |
| `blur_check.py` | AI/ML | Cổng chất lượng ảnh (cần opencv-python) |
| `fdi_parser.py` | AI/ML | Đọc số răng FDI từ văn bản VI/EN |
| `pii_redact.py` | AI/ML | Che PII lớp đầu trước khi gọi LLM |
| `pseudonymize.py` | DE | Giả danh hóa HMAC cho analytics |
| `dq_check.py` | DE | Kiểm tra chất lượng dữ liệu theo rule |
| `check_glb_regions.py` | FE | Mesh trong GLB khớp `region_code` |
| `scan_log_for_pii.py` | Security | Quét log tìm PHI/PII |
| `release_gate.py` | QC | Tính GO/NO-GO từ metrics |
| `error_budget.py` | SRE | Error budget và burn rate |
| `release_gate.py` (cập nhật) | QC | 21 mục kiểm RG-01…RG-21 (thêm an toàn lâm sàng, claims, RDR, pentest, license, chi phí AI, i18n) |
| `hazard_risk_check.py` | CSO | Kiểm hazard log: thiếu kiểm soát, rủi ro tồn dư không chấp nhận được |
| `claims_lint.py` | Regulatory | Tìm tuyên bố rủi ro (chẩn đoán, phát hiện bệnh…) VI/EN, không phân biệt dấu |
| `fhir_bundle_check.py` | Clinical Informaticist | Kiểm FHIR Bundle, định dạng ICD-10, check digit LOINC, số răng FDI |
| `license_register_check.py` | Data Curator | Kiểm sổ license (NC/DUA/SA, quá hạn rà soát) |
| `kappa.py` | Data Curator | Cohen's kappa giữa hai người gán nhãn |
| `sample_size.py` | Data Curator | Cỡ mẫu đánh giá theo khoảng tin cậy |
| `leakage_check.py` | Data Curator | Phát hiện trùng giữa tập train và golden |
| `cost_model.py` | MLOps | USD/tài liệu, USD/tháng, điểm hòa vốn tự host |
| `threshold_tuner.py` | MLOps | Chọn ngưỡng chuyển tầng M → L |
| `dicom_deid_check.py` | Medical Imaging | Kiểm DICOM còn thông tin định danh (cần pydicom) |
| `label_map_check.py` | Medical Imaging | Kiểm map nhãn segmentation → region_code |
| `registration_error.py` | Medical Imaging | Sai số căn chỉnh (TRE) |
| `glb_budget_check.py` | 3D Artist | Dung lượng, số tam giác, tên mesh của GLB |
| `svg_region_check.py` | 3D Artist | id trong SVG khớp region_code |
| `i18n_check.py` | Technical Writer | So file ngôn ngữ VI/EN: thiếu key, placeholder, chưa dịch |
| `ticket_stats.py` | Support | SLA, thống kê ticket, kiểm cổng G5-H |

## 6. Lưu ý an toàn
Sản phẩm chỉ minh họa và giải thích — mọi skill đều cấm nội dung chẩn đoán, liều thuốc, tiên lượng. Không đưa dữ liệu bệnh nhân thật vào môi trường dev/staging, log, prompt gửi ra ngoài hay ví dụ. Nội dung pháp lý chỉ để học tập, không phải tư vấn luật.

---

## English summary
A pack of **23 Anthropic-format Agent Skills** (v1.1 adds 9 roles from Part III of the plan: clinical safety, regulatory/privacy, clinical informatics, data curation, MLOps, medical imaging, 3D medical art, technical writing, support), one per MediLens role, plus `medilens-orchestrator`, which routes any problem to the owning role, writes task briefs and enforces hand-off gates. Each skill has a `SKILL.md` (frontmatter + workflow selector), `references/` (loaded on demand; every skill carries `project-context.md`), `assets/` (templates, code skeletons) and `scripts/` (runnable tools).

Install: copy skill folders to `~/.claude/skills/` or the repo's `.claude/skills/` for Claude Code; upload the per-skill zips from `dist/` in claude.ai or via the Skills API. Frontmatter uses only portable fields (`name`, `description`, `license`, `compatibility`, `metadata`).

The orchestrator now has 16 playbooks (PB-01…PB-16) and 112 routing rows; release checks are named RG-01…RG-21 so they never clash with phase gates G0…G6.

Safety: the product illustrates and explains; no diagnosis, dosing or prognosis. Never use real patient data outside production. Legal content is educational, not legal advice.
