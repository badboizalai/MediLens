# Digital record import (v1.5)

## Detection
- PDF: if every page has extractable text with ≥ 50 characters and the text is not garbage (ratio of letters ≥ 0.6), use the text layer; else route the page to OCR. Mixed PDFs are handled page by page.
- DOCX: python-docx paragraphs + tables; images inside DOCX go to OCR as separate pages.
- FHIR: JSON with `resourceType: Bundle`; run `fhir_bundle_check.py`; map without LLM (BR-045).

## Security (with security engineer)
Quarantine + malware scan first; PDF parsing in the worker sandbox (no network); reject PDFs with JavaScript/launch actions and DOCX with macros (`vbaProject.bin`) or external relationships; size and page limits per BR-010.

## Extraction
Text from digital records still goes through LLM extraction (schema per Unit) unless it is FHIR; tables keep row/column structure in the prompt; citations reference page + character offsets instead of bounding boxes.

## Provenance and conflicts
`sourceType = record`, document id, page; duplicates across photo and digital copy of the same record are merged by date + content hash; conflicts follow BR-044.
