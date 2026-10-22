# Requirements traceability

`traceability.csv` links each business rule (BR) to a user story (US) and a planned test case (TC).
Source of the rules: `docs/brd/business-rules.md`.

| Column | Meaning |
|---|---|
| `br_id` | Rule code, must exist in `business-rules.md` |
| `us_id`, `us_title` | Story id (`US-nnn`) and short title. Ids are placeholders until the story backlog is written |
| `tc_id`, `tc_level` | Test id (`TC-nnn`) and level: `unit`, `api`, `e2e` or `manual` |
| `test_idea` | One-line test idea (copied from the BRD "test idea" column) |
| `status` | `planned`, `implemented`, `passed` or `failed` |

All 32 rows are `planned`: no test exists yet.

## Run

```
python3 .claude/skills/medilens-business-analyst/scripts/check_traceability.py \
  docs/requirements/traceability.csv docs/brd/business-rules.md
```

The script only checks that every BR code has at least one story and one test row, and lists rows with `status=failed`.
"100%" means every rule has a test row, not that tests exist or pass. It exits 1 on any gap or failure.
The `BR-0TBD-*` placeholder groups are not matched (they are not `BR-nnn`), so they are not required until assigned.

## Update

1. Add or change a rule in `docs/brd/business-rules.md`, then add a row (one rule may have several rows).
2. Move `status` forward as the test is written and run; mark `failed` when it fails.
3. Re-run the script before opening the PR.
