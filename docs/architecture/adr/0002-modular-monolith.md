# ADR-001: Modular monolith with an AI worker

- **Status:** Proposed
- **Date:** 2026-10-23
- **Deciders:** Solution Architect (reviewers: security-engineer, mlops-engineer)
- **Related:** NFR-01, NFR-03, NFR-05, NFR-12, NFR-15; ADR-002, ADR-004, ADR-005, ADR-010, ADR-016, ADR-017 (plan §16.3)

## Context
MediLens is built and operated by one person at the start (see ADR-0001). The system has an API, a CPU/GPU-heavy OCR/LLM pipeline, a PHI boundary and a viewer backend. We need module isolation (PHI, AI egress) without the operational cost of many deployables. Budget target is NFR-15 (<= 100 USD/month at 100 MAU).

## Options considered
1. Microservices per bounded context: independent scaling and failure isolation; but network/ops overhead, distributed transactions, high cost for one developer, harder local dev.
2. Plain (unstructured) monolith: fastest start; but coupling grows, PHI/AI boundaries leak, extraction later is expensive.
3. Modular monolith (FastAPI) plus a separate worker process for OCR/LLM jobs on SQS: one codebase and DB, enforced module boundaries, AI load scaled independently. Needs discipline and tooling to keep boundaries.

## Decision
Option 3. Modules talk only through `application` services and domain events (transactional outbox, ADR-010); import-linter enforces this in CI. API and worker are separate ECS services built from the same codebase, so OCR/LLM load scales on queue depth without scaling the API (NFR-03, NFR-05). PHI Service and AI Gateway stay separate deployables because their trust boundaries differ (ADR-016, ADR-017).

## Consequences
- Positive: low ops cost; atomic transactions; simple local stack (`make up`); modules can later be extracted along existing event seams.
- Negative / trade-offs: shared DB and release train; a bad module can still exhaust shared resources (mitigated by separate queues and worker service).
- Follow-up tasks: import-linter contracts per module; module ownership map; load test of API vs worker scaling.

## Exit strategy
Extract a module behind its application-service interface and outbox events into its own service; per-module DB schemas (no cross-module joins) keep the split cost bounded.

## Revisit when
More than 3 developers, a module needs independent scaling or release cadence, or import-linter violations recur.
