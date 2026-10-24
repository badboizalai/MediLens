# Prompt extract-v2 (S7-T61)

Same files as `extract-v1` plus:

| File | Change vs v1 |
| --- | --- |
| `system.txt` | pages are shown as `[L<n>]` lines; every non-null field must also return `source.lines` (line ids); no bbox from the LLM; calibrated confidence; BR-042 wording |
| `extract.user.txt` | adds one synthetic worked example per Unit (`examples/<unit>.txt`, fake patient "Nguyen Van Test") |

Citations: `source.quote` is verified against OCR text (unchanged). `source.lines` is consumed in code (`extraction/service.py: anchor_lines`): it is removed before schema validation and replaced by `source.bbox` copied from the OCR line boxes. An unknown line id flags the field `line_id_unknown` and drops the bbox; the model never invents coordinates.

`extract-v1` stays untouched for golden-set comparison. Promotion needs a golden-set eval and review by security-engineer and clinical-safety-officer (see v1 README).
