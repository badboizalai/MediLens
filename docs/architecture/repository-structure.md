# Repository structure

```
medilens/
├── CLAUDE.md                  # Instructions for Claude Code (read every session)
├── README.md  CONTRIBUTING.md  SECURITY.md  LICENSE  Makefile
├── pyproject.toml  package.json  pnpm-workspace.yaml     # uv + pnpm workspaces
├── .claude/
│   ├── settings.json          # shared permissions (deny real-data paths, terraform apply)
│   ├── agents/                # medilens-skill-router — picks skills for a task
│   ├── commands/              # /route /new-unit /check-skills
│   └── skills/                # 23 role skills: medilens-<role>/{SKILL.md,references,assets,scripts}
├── .vscode/                   # settings, extensions, tasks, launch configs
├── .github/                   # workflows (CI), CODEOWNERS, PR/issue templates, dependabot
├── apps/
│   ├── web/                   # Next.js 15 (VI/EN) + 3D/2D viewer
│   ├── api/                   # FastAPI modular monolith (hexagonal modules)
│   ├── worker/                # AI pipeline worker (OCR → LLM → materialize)
│   ├── ai-gateway/            # provider calls, redaction, cascade routing, cost
│   └── phi-service/           # isolated PHI service / key hierarchy
├── packages/
│   ├── anatomy-assets/        # GLB, SVG, unit configs (names == region_code)
│   ├── api-client/            # generated TS client
│   └── design-system/         # tokens + UI primitives
├── ml/        {datasets,eval,notebooks,registry}   # synthetic data, golden set, model registry
├── imaging/                   # DICOM de-id, segmentation, mesh, registration (v2)
├── data/      {dbt,flows,catalog}                   # medallion pipelines, contracts, license register
├── infra/     {terraform,docker,helm,docker-compose.yml}
├── regulatory/                # intended use, RDR, claims review, AI impact assessments
├── safety/                    # clinical risk plan, hazard log, safety case
├── docs/
│   ├── plan/                  # master plan (VI/EN, md+pdf) and 52-week sprint plan (xlsx)
│   ├── agents/                # canonical project-context.md, skill-catalog.md, skill-pack readme
│   ├── architecture/          # C4, repository structure, adr/
│   ├── requirements/ brd/ srs/ user-guide/ runbooks/ security/ threat-model/ operations/
├── tests/     {e2e,load}      # cross-app tests
└── tools/                     # validate/sync/package skills
```

## Conventions
- **One owner per folder** (see CODEOWNERS and the routing matrix). Folder → owner skill: `apps/api`→backend, `apps/web`+`packages/design-system`→frontend/UX, `apps/worker`+`ml`→AI/ML, `data`→data-engineer, `infra`→cloud-devops, `imaging`→medical-imaging, `packages/anatomy-assets`→3D artist, `safety`→CSO, `regulatory`→regulatory-privacy, `docs/runbooks`→SRE, `tests`→QA.
- **Dependency direction**: apps depend on packages; packages never depend on apps. API modules are independent of one another.
- **Single source for shared context**: `docs/agents/project-context.md` → copied into each skill by `tools/sync_skill_context.py`; CI fails if out of sync.
- **Real data never enters the repo** (`.gitignore` + Claude deny rules).
- **Decisions** are ADRs in `docs/architecture/adr/` (template: `medilens-solution-architect/assets/adr-template.md`).
