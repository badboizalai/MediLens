# ADR-006: Hybrid OCR (local PaddleOCR/VietOCR with cloud/LLM vision baseline)

- **Status:** Proposed
- **Date:** 2026-10-23
- **Deciders:** Solution Architect (reviewers: security-engineer, mlops-engineer)
- **Related:** NFR-04, NFR-09, NFR-14, NFR-15; SEC-AR-04; ADR-007, ADR-012, ADR-017, ADR-021 (plan §7, §16.3)

## Context
Records are Vietnamese and English: printed, scanned and handwritten. Images are PHI, so sending every page to a third party is undesirable (NFR-09). AWS Textract does not support Vietnamese. Accuracy must be measured on a golden set (CER, field F1) before we commit. Cost target is AI <= 0.10 USD/doc (NFR-15) and 95% of documents < 2 min (NFR-04).

## Options considered
1. Self-hosted only (PaddleOCR + VietOCR): data stays in our VPC, zero token cost, CPU-friendly; weak on handwriting and degraded scans, we own tuning and serving.
2. Cloud OCR only (Textract / Google Document AI / Azure DI): strong layout/tables, little ops; Textract lacks Vietnamese, other vendors move PHI out of AWS and add vendor assessment and overseas-transfer burden.
3. Vision LLM only (Bedrock): handles handwriting and layout in one call; highest per-page cost and latency, hallucination risk on numbers, model availability varies by region (ADR-012).
4. Hybrid: PaddleOCR/VietOCR primary; low-confidence or handwritten pages escalate to a Bedrock vision model through the AI Gateway; Textract only for English documents if it beats local on the golden set. Cloud engines also serve as the accuracy baseline.

## Decision
Option 4 behind an `OcrProvider` interface (adapters `PaddleOcr`, `BedrockVision`, optional `TextractOcr`, `Fake` for tests) so a provider swap takes <= 2 days (NFR-14). Escalation is driven by confidence thresholds in the model cascade (ADR-021); handwriting is always flagged low confidence for user review. Every vision-LLM call goes through the AI Gateway with redaction, quota and cache (ADR-017). Thresholds and the Textract-English decision are set from golden-set results, not assumed.

## Consequences
- Positive: most pages cost no tokens and stay local; handwriting still covered; providers swappable.
- Negative / trade-offs: two code paths to evaluate and monitor; local OCR needs CPU (GPU under load) and model packaging; threshold tuning needed.
- Follow-up tasks: build golden set (synthetic only); measure CER/field F1 per engine; choose escalation thresholds; confirm vision model choice after ADR-012.
- VERIFY: which Bedrock vision-capable models are available in the chosen region and their Vietnamese handwriting quality.
- VERIFY: whether Textract English accuracy justifies its use over PaddleOCR.

## Exit strategy
Replace an adapter via the `OcrProvider` interface and re-run the golden-set evaluation; no schema change since outputs normalise to `OcrResult`.

## Revisit when
Golden-set accuracy plateaus below target, escalation exceeds 15% of pages, or cost per document exceeds NFR-15.
