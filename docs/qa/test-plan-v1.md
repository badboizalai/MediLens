# Test Plan - Release v1 (MVP)

Status: draft. Strategy: `test-strategy.md`.

1. **Scope.** In: upload (photo/PDF/digital/text), OCR and extraction, review screen, 2D/3D viewer, auth, consent, sharing, i18n VI/EN, AI evaluation, authz. Out: CT/DICOM (v2), production load beyond NFR scenarios.
2. **References.** `docs/plan/project-plan.en.md` (section 10.1), `docs/requirements/traceability.csv`, `RULES.md`, `safety/hazard-log.csv`.
3. **Risks and focus.** Strategy section 2: PHI access, AI correctness and medical-safety wording are very high.
4. **Levels and types.** Unit, integration (Testcontainers), contract/API, authz, E2E (Playwright), a11y (axe), k6, AI evaluation, claims lint, hazard check. Commands: `make test`, `make governance`, `make load`; E2E per `tests/e2e/README.md`.
5. **Environments and data.** local, CI, staging; synthetic data only (strategy sections 3-4).
6. **Entry criteria.** Acceptance criteria exist; build deployed to the test env; synthetic data ready.
   **Exit criteria.** Strategy section 7: all MUST TCs pass, no open S1/S2, coverage >= 70% (domain >= 85%), AI gates met, axe 0 serious, security suites pass, summary report filed.
7. **Schedule.** Per sprint: day 1 review ACs and derive TCs; days 2-8 automate alongside dev; day 9 regression and exploratory; day 10 summary. Pre-release: full regression, k6, AI golden-set run, then QC release gate.
8. **Deliverables.** Test cases (`test-case-template.md`), automation in repo, traceability CSV kept current, AI evaluation report, test summary report.
9. **Defect management.** Severity/priority per strategy section 9; reports use `bug-report-template.md`; triage twice weekly, daily in the week before release.
10. **Reporting.** Daily status in the sprint channel; test summary report per release: pass rates, open defects by severity, coverage, AI metrics vs gates, quarantined tests, BR without a passing TC.

## Initial automation backlog
| Id | Item | Level | Status |
| --- | --- | --- | --- |
| E2E-SMOKE | Public home loads and shows disclaimer | E2E | skeleton in `tests/e2e` |
| AUTHZ-ALL | Authz test per endpoint | API | planned |
| AI-GATE | Golden-set CER/F1 gate in CI | ML eval | planned |
| A11Y-HOME | axe on home and review screen | E2E | planned |
| LOAD-API | k6 beyond `/healthz` smoke | load | planned |
