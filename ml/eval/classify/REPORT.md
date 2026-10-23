# Page classifier (rules) - golden-v1 evaluation

- Pages: 150 (golden-v1, seed 20261001, clean text, one page per record)
- Accuracy: **1.000** (150/150); target >= 0.90
- Below LLM fallback threshold (0.5): 0

## Confusion (true -> predicted : count)

- dental_record -> dental_record: 50
- outpatient_form -> outpatient_form: 100

## Misclassified ids

- none

## Caveats

- golden-v1 carries no page-type labels; labels are derived from `unit` (see script).
- Only 2 of the 9 types occur (dental_record, outpatient_form); the other 7 are covered
  only by unit-test snippets in `apps/worker/tests/classify`. Accuracy here is optimistic:
  one template per unit, clean text, no OCR noise. Re-run on real-OCR text and on a
  9-type labelled set (plan 25.1: 30 per type) before relying on it.
