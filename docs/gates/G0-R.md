# Gate G0-R - Regulatory: evidence pack

> Draft prepared by AI (owner skill: medilens-qc-release-gatekeeper; reviewers: product-manager, regulatory-privacy-officer). **Educational, not legal advice. AI does not sign gates.** Version 0.1, 2026-10-23.

**Criterion (plan):** Intended Use Statement + Regulatory Decision Record approved; forbidden-claims list. **Approver:** REG (human).

**Readiness: NOT YET READY.** Documents exist as drafts, all merged. RDR-001 itself states it requires human REG sign-off; its tentative decision (outside medical-device scope for v1, illustrative/educational software) is conditional and unverified against current Vietnamese rules.

Evidence cites repo paths; the merged PR number is in parentheses (`https://github.com/badboizalai/MediLens/pull/<n>`).

## 1. Checklist
| # | Criterion item | Evidence | Status | Gap | Owner |
| --- | --- | --- | --- | --- | --- |
| 1 | Intended Use Statement | `regulatory/intended-use.md` (v0.1-draft, #4) | partially met | Draft, merged; not reviewed by a human REG; `VERIFY:` items open | regulatory-privacy-officer |
| 2 | Regulatory Decision Record | `regulatory/RDR-001.md` (#4) | partially met | Tentative decision "outside medical-device scope for v1", conditional. Legal basis (Decree 98/2021 as amended, Circular 05/2022) needs verification by REG or counsel; CT (v2), commercialisation and hospital work are "Undetermined - seek advice" | human REG / counsel |
| 3 | Forbidden-claims list | `regulatory/forbidden-claims.md` (#4) | partially met | Draft, merged; needs REG and CSO review | regulatory-privacy-officer, clinical-safety-officer |
| 4 | Claims enforced in tooling (supporting) | Claims lint with BR-042 boundary phrases, `.claude/skills/medilens-regulatory-privacy-officer/scripts/claims_lint.py` (#19) | partially met | Merged; lint is a safety net, not a legal review | regulatory-privacy-officer |
| 5 | Privacy position (supporting) | `regulatory/privacy/DPIA-v0.md`, `OTIA-decision.md`, `data-inventory.md` (#12) | partially met | Draft; DPO named as `VERIFY:`; overseas-transfer filing steps need a lawyer; not strictly G0-R but gates real data | human DPO/REG |
| 6 | Licence position (supporting) | `data/license-register.csv`, `data/catalog/sources.md` (#2) | partially met | Covers planned sources only; REG co-sign pending (`reg_cosign` column empty); G1-D is separate | data-curator |
| 7 | Clinical safety linkage (supporting) | CRMP and hazard log `safety/CRMP.md`, `safety/hazard-log.csv` (#3) | partially met | Draft hazard log; CSO sign-off belongs to G2-CS | clinical-safety-officer |
| 8 | Human REG verification | None | **not met** | No human has reviewed or signed any regulatory document | human REG |

Counts: met 0, partially met 7, not met 1 (row 8, blocks GO).

## 2. What remains before GO (exact list)
1. Review the merged drafts (#4, and #12, #19 if used as evidence); merge is not approval.
2. Human REG verifies every `VERIFY:` item, confirms or changes the RDR-001 decision, and approves the Intended Use Statement and forbidden-claims list.
3. Decide whether external legal advice is needed (RDR already flags it for CT, commercialisation, hospital data).
4. Confirm approver set: plan sheet says REG; orchestrator protocol says steering. PM to rule.
5. Sign the table below.

## 3. Findings to carry forward
- G0-R must be re-run before CT features (plan gate G0-R (CT), S21, RDR-002, REG + CSO).
- Any change to user-facing wording (app, marketing) must pass the forbidden-claims list and BR-042.

## 4. Sign-off (humans only)
| Role | Name | Decision (GO / NO-GO / GO with conditions) | Conditions | Signature | Date |
| --- | --- | --- | --- | --- | --- |
| REG (regulatory-privacy-officer, human) | | | | | |
| PM (countersign, if steering rule applies) | | | | | |
| QC (evidence check) | | | | | |

## 5. Version history
| Version | Date | Author | Note |
| --- | --- | --- | --- |
| 0.1 | 2026-10-23 | AI (qc-release-gatekeeper), S2-T15 | Initial pack; unsigned |
| 0.2 | 2026-10-23 | AI (qc-release-gatekeeper), S2-F11 | Repo paths replace PR refs; licence row downgraded to partially met (REG co-sign pending); unsigned |
