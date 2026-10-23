# Hazard log v1 notes (S7-T68)

**DRAFT. Prepared by an AI agent. Every row below is `draft-pending-CSO`; nothing is approved. Review and sign-off by the Clinical Safety Officer (human) is a required gate before G2-CS.**

Scale: `CRMP.md` sections 2 to 4. Verify with `python3 .claude/skills/medilens-clinical-safety-officer/scripts/hazard_risk_check.py safety/hazard-log.csv --strict`.

## Changed rows (same ids, no duplicates)
| id | Change | Evidence on main |
| --- | --- | --- |
| HZ-001 wrong side | Added CS-033; verification lists implemented vs planned | `data/terminology/tests/test_region_tree.py::test_laterality_consistent`; BR-012 gate tests |
| HZ-002 wrong region | Added CS-034 | `test_region_tree.py` (closed tree); BR-015 mapper still planned |
| HZ-003 read as diagnosis | Added CS-035 (BR-042) | `claims_lint.py` in `make lint`; banner still planned |
| HZ-006 unconfirmed shown as fact | Added CS-036 | `apps/api/tests/extraction/test_review.py::test_confirm_blocked_until_low_confidence_confirmed` |
| HZ-014 mix-up / other person | Evidence added | `test_other_users_document_and_field_are_404`, `test_unauthenticated_is_401` |
| HZ-015 OCR digit error | Evidence added | BR-012 gate tests |

## New rows
| id | Hazard | Initial | Residual (target) |
| --- | --- | --- | --- |
| HZ-017 | Critical field missed or omitted (unreviewed low-confidence value; field dropped by extraction) | 9 ALARP | 6 ALARP |
| HZ-018 | needs_retake / failed status not surfaced | 6 ALARP | 3 acceptable |
| HZ-019 | Upload of someone else's record (consent / identity) | 8 ALARP | 4 acceptable |

## Points for the CSO
- Residual values assume the planned controls land; the implemented-only residual is higher for HZ-001, HZ-002, HZ-003, HZ-019 (golden sets, mapper, banner, identity check are not on main).
- A confidently wrong value (right format, confidence >= 0.7) passes the BR-012 gate unreviewed (HZ-001, HZ-015, HZ-017).
- Spec mismatch: BR-012 says 422 `/errors/unconfirmed-fields`; the API returns 409 with field ids.
- HZ-005 (S5 residual) still needs explicit CSO sign-off; unchanged.
- Information-only controls (banner, labels) are not relied on for S >= 4 rows.
