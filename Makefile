.DEFAULT_GOAL := help
COMPOSE := docker compose -f infra/docker-compose.yml --env-file .env

help: ## Show targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-16s\033[0m %s\n",$$1,$$2}'

setup: ## First-time setup (env file, deps, hooks)
	@test -f .env || cp .env.example .env
	uv sync --all-packages
	pnpm install
	pre-commit install

up: ## Start local stack (postgres, redis, minio, keycloak, mailpit)
	$(COMPOSE) up -d
down: ## Stop local stack
	$(COMPOSE) down
api-dev: ## Run API with reload
	cd apps/api && uv run uvicorn medilens.main:app --reload --port 8000
web-dev: ## Run web dev server
	pnpm dev
worker-dev: ## Run worker
	cd apps/worker && uv run python -m medilens_worker.main
migrate: ## Apply DB migrations
	cd apps/api && uv run alembic upgrade head
api-client: ## Regenerate TS client from OpenAPI (API must be running)
	pnpm dlx openapi-typescript http://localhost:8000/openapi.json -o packages/api-client/src/schema.d.ts

lint: ## Lint Python + TS + skills
	uv run ruff check . && uv run ruff format --check .
	pnpm lint
	$(MAKE) skills-check
api-lint: ## Architecture rules (import-linter)
	cd apps/api && uv run lint-imports
format: ## Auto-format
	uv run ruff check --fix . && uv run ruff format .
	pnpm format
typecheck: ## Type checks
	pnpm typecheck
test: ## Run all unit tests
	uv run pytest
	pnpm test
e2e: ## Playwright E2E
	pnpm --filter @medilens/web e2e
load: ## k6 load test
	k6 run tests/load/smoke.js

skills-check: ## Validate skills/agents and refresh catalog
	python3 tools/validate_skills.py
	python3 tools/build_skill_index.py
skills-sync: ## Sync canonical project-context into all skills
	python3 tools/sync_skill_context.py
skills-package: ## Zip each skill into dist/skills
	tools/package_skills.sh
governance: ## Run the CI governance checks locally
	python3 tools/validate_skills.py
	@tests=$$(ls .claude/skills/*/scripts/test_*.py 2>/dev/null); \
	if [ -n "$$tests" ]; then uv run --with pytest pytest $$tests; else echo "no skill script tests found"; fi
	python3 .claude/skills/medilens-clinical-safety-officer/scripts/hazard_risk_check.py safety/hazard-log.csv
	python3 .claude/skills/medilens-data-curator/scripts/license_register_check.py data/license-register.csv
	@paths=""; for p in regulatory docs/ux apps/web/messages; do [ -e "$$p" ] && paths="$$paths $$p"; done; \
	[ -z "$$paths" ] || python3 .claude/skills/medilens-regulatory-privacy-officer/scripts/claims_lint.py $$paths

.PHONY: help setup up down api-dev web-dev worker-dev migrate api-client lint api-lint format typecheck test e2e load skills-check skills-sync skills-package governance
