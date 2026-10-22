# Clinical Content and Display Review Standard

## Contents
1. Wording
2. Viewer and colour
3. Special anatomy and sources
4. Knowledge articles
5. AI explanations
6. Review outcomes

## 1. Wording
- Describe what the record says ("Your record mentions…"), never what the user has ("You have…") unless quoting the record.
- No verbs of diagnosis or detection in UI or marketing; run the regulatory skill's `claims_lint.py`.
- Plain language, short sentences, define every medical term on first use; avoid alarming adjectives.
- Always offer the next safe step: "Ask your doctor about…", "Call 115 if…".

## 2. Viewer and colour
- Severity colour always paired with a text label and legend (BR-020); never red-only meaning.
- Show the source snippet/bounding box for every confirmed finding.
- Summary mode is the default for oncology; detail on request.
- Metastasis or spread is shown only when the record states it (BR-021); "possible spread" lives in educational content, visually separate.

## 3. Special anatomy and sources
- Resected organ: hidden or ghosted with label "đã cắt bỏ / removed (per record)".
- Implant/device: glyph with name; never coloured as a finding.
- Variant or unknown side: show at organ level with `precision` badge; never guess a side.
- `patient_reported`: neutral style, "bạn mô tả / you described", no ICD code, no severity colour (BR-040).
- `image_derived` (CT): "illustration from your CT, not a radiology result" watermark (BR-042).
- Conflicts: mismatch warning naming both sources (BR-044).

## 4. Knowledge articles
Source (guideline, textbook, reputable public health body) cited; reviewer and review date; no dosing, no prognosis numbers; reading level appropriate; VI and EN versions reviewed separately for meaning.

## 5. AI explanations
Answer only from approved articles + the user's own confirmed data; cite sources; refuse dosing, medication changes, prognosis, diagnosis; emergency routing first; uncertainty stated plainly.

## 6. Review outcomes
Approved · Approved with changes (numbered list, re-check by owner) · Rejected (reason + hazard id). Record with `assets/clinical-review-record-template.md`.
