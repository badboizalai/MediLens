# CI/CD Pipeline

## Branching
Trunk-based: short branches → PR → main. Conventional Commits; semantic-release generates changelog and tags.

## CI stages (PR) and gates
| Stage | Tools | Gate |
| --- | --- | --- |
| Lint/format | ruff, eslint, prettier, terraform fmt | fail on error |
| Types | mypy (domain strict), tsc | fail |
| Unit tests | pytest, vitest | fail; coverage thresholds |
| Integration | pytest + Testcontainers + LocalStack | fail |
| Contract | schemathesis, oasdiff breaking | fail on breaking without version |
| SAST | Semgrep (custom rules: no PHI logging, no raw SQL), CodeQL | High/Critical fail |
| SCA | Trivy fs / Dependabot | Critical fail |
| Secrets | gitleaks | any fail |
| IaC | tflint, Checkov | High fail |
| Build | docker buildx (arm64) | — |
| Image scan + SBOM | Trivy image, Syft (CycloneDX) | Critical fail |
| AI eval (path filter `ml/**`, `prompts/**`) | eval harness on golden set | regression > 1 F1 point fail |
| E2E (mocked) | Playwright + MSW | fail |

## CD
main merge → build once → push ECR `:<sha>` (immutable tags) → sign (cosign, optional) → deploy staging (migrations task, then services) → smoke + E2E against staging → **manual approval** (GitHub environment `production`) → prod blue/green or rolling with circuit breaker → post-deploy synthetic checks → release notes.

## Environments & approvals
GitHub environments: `staging` (auto), `production` (required reviewer = you, wait timer 5 min). OIDC role per environment with trust condition `repo:<org>/medilens:environment:production`.

## DORA metrics
Deployment frequency, lead time (commit → prod), change failure rate (deploys causing incident/rollback), MTTR — collected from deployment records and incidents.
