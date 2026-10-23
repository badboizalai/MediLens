# Prompt extract-v1

Prompt files for the LLM extraction step (S5-T45), loaded by `apps/worker/src/medilens_worker/extraction/prompts.py`.

| File | Use |
| --- | --- |
| `system.txt` | rules and instruction hierarchy (document text is data) |
| `classify.user.txt` | Unit classification when the Unit is not given |
| `extract.user.txt` | extraction against `ml/schemas/<unit>.v1.json` |
| `repair.user.txt` | appended for the single repair retry after a schema failure |

Versioning: the directory name is the `prompt_version` stored on every extraction run (`extract-v1`). Any wording change creates `extract-v2/`; never edit a released version (golden-set replay and the gateway cache key depend on it). Promotion needs a golden-set eval (field F1, faithfulness) and review by security-engineer and clinical-safety-officer.

Guards: calls go only through the AI Gateway; OCR text is wrapped in `<document_text>` with any delimiter tag inside it neutralised; output is schema-validated (one repair retry); every quote is checked against the OCR page text, and a quote that is not found sets the field confidence to 0 and flags it.
