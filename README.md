<div align="center">

# MediLens

**Hiểu hồ sơ y tế của chính mình — nhìn thấy nó trên cơ thể 3D/2D.**
*Understand your own medical records — see them on a 3D/2D body model.*

![status](https://img.shields.io/badge/status-pre--alpha-orange)
![python](https://img.shields.io/badge/python-3.10-blue)
![node](https://img.shields.io/badge/node-20%2B-green)
![license](https://img.shields.io/badge/license-proprietary-lightgrey)

[Tiếng Việt](#tiếng-việt) · [English](#english) · [Docs](docs/) · [Kế hoạch / Plan](docs/plan/)

</div>

> ⚠️ **Safety / An toàn:** MediLens *minh họa và giải thích*; **không chẩn đoán, không kê liều, không tiên lượng** (BR-042). Không dùng dữ liệu bệnh nhân thật ngoài production. Nội dung pháp lý chỉ để học tập, không phải tư vấn luật.

---

## Tiếng Việt

### Giới thiệu
MediLens là web app giúp bệnh nhân **hiểu hồ sơ y tế của mình**: quét hồ sơ (OCR) → AI trích xuất chẩn đoán, vị trí tổn thương, số đo → hiển thị trên **mô hình cơ thể 3D/2D** và sơ đồ cơ quan theo từng khoa, kèm **dòng thời gian trước/sau**. Dự án vận hành như một dự án doanh nghiệp (quy trình, tài liệu, test, bảo mật, vận hành) nhưng do một người đảm nhiệm mọi vai trò, với **23 AI skill theo role** hỗ trợ.

### Tính năng chính
| Nhóm | Nội dung |
| --- | --- |
| Tài khoản | Email + Google OAuth, MFA, nhiều hồ sơ bệnh nhân / một tài khoản |
| Tài liệu | Upload ảnh/PDF, OCR tiếng Việt + Anh, trích xuất có cấu trúc, **màn hình review** (người dùng luôn xác nhận) |
| Viewer | 2D + 3D tô màu theo `region_code`; Unit đầu tiên: **Nha khoa (FDI), Tim mạch, Ung bướu** |
| Giải thích | LLM + RAG có trích dẫn nguồn và disclaimer |
| Theo dõi | Timeline trước/sau, chia sẻ có thời hạn với bác sĩ/người thân |
| Vận hành | Audit log, admin, RLS theo `profile_id`, mã hóa field nhạy cảm |

Kiến trúc 3 cấp **Khoa → Unit → Vùng giải phẫu**: thêm Unit mới chỉ bằng cấu hình + asset, không sửa core.

### Mục tiêu đo được
| # | Mục tiêu | Thước đo |
| --- | --- | --- |
| G1 | Thấy tổn thương trên mô hình cơ thể | ≥ 85% tài liệu test trích xuất & map đúng vùng |
| G2 | Giải thích dễ hiểu, không thay bác sĩ | 100% câu trả lời AI có nguồn + disclaimer |
| G3 | Theo dõi tiến triển | Timeline ≥ 2 mốc cho cùng một finding |
| G4 | Hệ thống chuẩn doanh nghiệp | CI/CD, coverage ≥ 70%, SLO 99.5%, audit log đầy đủ |
| G5 | Học cách vận hành dự án lớn | Bộ tài liệu đầy đủ (BRD, SRS, ADR, runbook…) |

### Lộ trình
MVP **v1.0 tuần 32** → v1.5 tuần 40 (nhập bệnh án số, thư viện template giải phẫu, Hô hấp, Thận–Tiết niệu) → v2.0 tuần 52 (CT/DICOM, segmentation, mesh riêng từng bệnh nhân). Chi tiết 52 tuần / 26 sprint: [`docs/plan/MediLens_Sprint_Plan_52w.xlsx`](docs/plan/MediLens_Sprint_Plan_52w.xlsx). Mỗi giai đoạn kết thúc bằng một **gate** (G0…G6) — không qua gate, không sang giai đoạn sau.

## English

### Overview
MediLens helps patients **understand their own medical records**: OCR → AI extracts diagnoses, lesion locations and measurements → shown on a **3D/2D body model** per department with a **before/after timeline**. It is run like an enterprise project by one person, assisted by **23 role-based AI skills**.

### Highlights
Auth + profiles · photo/PDF upload with VI/EN OCR · structured extraction with mandatory human review · 2D/3D viewer coloured by `region_code` (Dental, Cardiology, Oncology in v1.0) · RAG explanations with citations · timeline & time-limited sharing · audit log, RLS, field-level encryption.

---

## Kiến trúc / Architecture

```
Browser ──▶ Next.js (apps/web) ──▶ FastAPI modular monolith (apps/api) ──▶ PostgreSQL 16 (+pgvector, RLS)
   │ presigned upload                    │ outbox → Redis queue                 ▲
   ▼                                     ▼                                      │
 S3 / object storage ◀────────── AI worker (apps/worker) ─▶ AI Gateway ─▶ OCR / LLM providers
                                         └─▶ PHI service (apps/phi-service, key hierarchy)
```
Worker không nhận request người dùng; kéo job từ Redis, đọc S3, ghi PostgreSQL. FE nhận trạng thái qua SSE. Quy tắc phụ thuộc: `api → application → domain`; module chỉ nói chuyện qua service/event (kiểm bằng `import-linter`).

### Tech stack
| Lớp | Lựa chọn |
| --- | --- |
| Frontend | Next.js 15, React 19, TypeScript, Tailwind, shadcn/Radix, TanStack Query, Zustand |
| 3D / 2D | Three.js + React Three Fiber + drei · SVG + D3 |
| Backend | Python 3.10, FastAPI, SQLAlchemy 2 + Alembic, Pydantic v2 |
| Worker / AI | Dramatiq (Redis), PaddleOCR + VietOCR, LLM qua AI Gateway, pgvector RAG |
| Dữ liệu | PostgreSQL 16, Redis 7, S3, dbt + Prefect/Dagster |
| Auth | Keycloak (OIDC) |
| Hạ tầng | Docker, Terraform, AWS (ECS Fargate, RDS, S3, SQS, KMS, CloudFront), GitHub Actions |
| Quan sát / Test | OpenTelemetry, Prometheus, Grafana, Sentry · pytest, Vitest, Playwright, k6 |

## Cấu trúc repo / Repo layout
```
.claude/        skills (23 role), agents (skill-router), commands, settings
apps/           web · api · worker · ai-gateway · phi-service
packages/       anatomy-assets · api-client · design-system
ml/ imaging/ data/   AI eval & registry · DICOM/mesh (v2) · dbt & contracts
infra/          docker-compose · terraform (dev/staging/prod)
regulatory/ safety/  hồ sơ pháp lý · an toàn lâm sàng
docs/ tests/ tools/  tài liệu · e2e/load · script quản lý skill
```
Chi tiết & chủ sở hữu từng thư mục: [`docs/architecture/repository-structure.md`](docs/architecture/repository-structure.md).

## Bắt đầu nhanh / Quick start

**Yêu cầu / Prerequisites:** Docker + Compose, [uv](https://docs.astral.sh/uv/) (quản lý Python **3.10**), Node 20+ & pnpm 9, make.

```bash
make setup      # tạo .env, uv sync (Python 3.10), pnpm install, pre-commit
make up         # postgres+pgvector, redis, S3 (SeaweedFS), keycloak, mailpit
make migrate    # Alembic
make api-dev    # http://localhost:8000/docs
make web-dev    # http://localhost:3000
make help       # tất cả lệnh
```
| Dịch vụ local | URL |
| --- | --- |
| API / OpenAPI | http://localhost:8000/docs |
| Web | http://localhost:3000 |
| Keycloak | http://localhost:8080 (admin/admin, chỉ dev) |
| S3 | http://localhost:9000 |
| Mailpit | http://localhost:8025 |

### Kiểm tra chất lượng
```bash
make lint        # ruff + eslint + validate skills
make api-lint    # import-linter (luật kiến trúc)
make test        # pytest + vitest
make e2e / load  # Playwright / k6
```

## Làm việc với Claude Code (agent chọn skill)
Mở thư mục trong VS Code, cài extension khuyến nghị. Claude đọc [`CLAUDE.md`](CLAUDE.md) và 23 skill trong `.claude/skills/`.
- `/route <việc cần làm>` — agent **`medilens-skill-router`** chọn skill chính + skill review + gate.
- `/medilens-<role> <yêu cầu>` — gọi trực tiếp một role (vd. `/medilens-backend-engineer`).
- `/new-unit <tên>` — thêm Unit mới end-to-end (playbook PB-02).
- `make skills-check` / `skills-sync` / `skills-package` — kiểm tra, đồng bộ context, đóng gói zip.

Danh mục skill: [`docs/agents/skill-catalog.md`](docs/agents/skill-catalog.md) · Hướng dẫn gói skill: [`docs/agents/skill-pack-readme.md`](docs/agents/skill-pack-readme.md).

## Quy ước / Conventions
Conventional Commits · mỗi endpoint mới có authz test · thay đổi schema = migration · quyết định = ADR · không dữ liệu thật trong repo/log/prompt. Xem [`CONTRIBUTING.md`](CONTRIBUTING.md), [`SECURITY.md`](SECURITY.md).

## Tài liệu / Documentation
| | |
| --- | --- |
| Kế hoạch tổng thể | [VI](docs/plan/project-plan.vi.md) · [EN](docs/plan/project-plan.en.md) (+PDF) |
| Lịch 52 tuần | [`MediLens_Sprint_Plan_52w.xlsx`](docs/plan/MediLens_Sprint_Plan_52w.xlsx) |
| Ngữ cảnh dự án | [`docs/agents/project-context.md`](docs/agents/project-context.md) |
| ADR | [`docs/architecture/adr/`](docs/architecture/adr) |

## License
Proprietary — personal learning project. Xem [`LICENSE`](LICENSE).
