# Seed Hazard Catalog

Initial S/P are for the uncontrolled design; residual values assume the listed controls are implemented and verified. Adjust per feature.

| ID | Hazard (situation → harm) | Causes | S | P | Controls (CS) | Residual S×P |
| --- | --- | --- | --- | --- | --- | --- |
| HZ-001 | Finding shown on the wrong side → user misinforms clinician or worries about wrong organ | OCR/LLM laterality error | 3 | 3 | CS-001 laterality rules + confidence; CS-002 user confirmation; CS-003 show source snippet | 3×1 |
| HZ-002 | Finding shown on wrong region | Mapping error, ambiguous text | 3 | 3 | CS-004 `unmapped` instead of guessing (BR-015); CS-005 region accuracy gate ≥ 0.85 | 3×1 |
| HZ-003 | User reads illustration as a diagnosis and self-treats | Wording, visuals | 4 | 3 | CS-006 no diagnostic wording (claims lint); CS-007 persistent "not a diagnosis" banner; CS-008 guardrails | 4×1 |
| HZ-004 | LLM explanation gives dosage or medication advice | Jailbreak, prompt injection | 4 | 3 | CS-009 guardrails block ≥ 95%; CS-010 red-team set in CI | 4×1 |
| HZ-005 | Emergency symptoms in text not routed to 115 | Missed keywords, language variants | 5 | 2 | CS-011 emergency detector with high recall, shown first (BR-041); CS-012 test set incl. dialect/no-accent text | 5×1 |
| HZ-006 | Unconfirmed extraction appears as fact | State bug | 3 | 2 | CS-013 only `confirmed` rendered (BR-013) + test | 3×1 |
| HZ-007 | Metastasis shown when the record does not state it | LLM inference | 4 | 3 | CS-014 BR-021 rule + schema requires source span | 4×1 |
| HZ-008 | Survival/prognosis statement shown | LLM | 4 | 2 | CS-015 topic block + output filter | 4×1 |
| HZ-009 | Severity colour misread (colour-blind, no label) | Design | 2 | 3 | CS-016 text label always (BR-020); contrast AA | 2×1 |
| HZ-010 | Resected organ still drawn → user believes organ present | Template mismatch | 3 | 3 | CS-017 `organ_status` hides/greys organ; label | 3×1 |
| HZ-011 | Implant/device not shown → confusion with findings | Missing device glyph | 2 | 3 | CS-018 device glyph library | 2×1 |
| HZ-012 | Patient-reported text displayed like a clinical finding | Styling | 3 | 3 | CS-019 BR-040 neutral style + "you described" tag | 3×1 |
| HZ-013 | Conflict between sources hidden | Merge logic | 3 | 2 | CS-020 BR-044 mismatch warning | 3×1 |
| HZ-014 | CT mesh read as a radiology result | Visual realism | 4 | 3 | CS-021 BR-042 illustration watermark; no measurements; CSO review | 4×1 |
| HZ-015 | Registration error places finding on wrong organ in CT view | Algorithm | 3 | 3 | CS-022 error < 15 mm gate; fallback to template | 3×1 |
| HZ-016 | Outdated KnowledgeArticle | Content ageing | 3 | 3 | CS-023 review date + cron reminder; overdue hidden | 3×1 |
| HZ-017 | Wrong lab unit/reference range → false alarm or reassurance | Normalisation | 3 | 3 | CS-024 show unit + original range from the record; never invent ranges | 3×1 |
| HZ-018 | Shared view seen by wrong person reveals sensitive diagnosis | Sharing bug | 4 | 2 | CS-025 BR-030/031 + Cedar tests; watermark | 4×1 |
| HZ-019 | Child profile shown with adult template/ranges | Template choice | 3 | 2 | CS-026 age-based template; paediatric caution banner | 3×1 |
| HZ-020 | Translation changes medical meaning (VI↔EN) | Localisation | 3 | 3 | CS-027 glossary-driven translation + CSO review of medical strings | 3×1 |
