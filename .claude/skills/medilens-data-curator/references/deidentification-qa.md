# De-identification QA

## Text (documents, donations)
- Automated: `pii_redact.py` (AI skill) + NER for names, addresses, phone, email, ID numbers, insurance numbers, record numbers, dates of birth (keep year), facility-specific identifiers.
- Checklist reference: the 18 HIPAA Safe Harbor identifier types are a useful completeness checklist even though Vietnamese law applies.
- Manual sample: 5% of items (min 20) per batch; any residual identifier → fix the rule, re-run the batch, re-sample.
- Record: batch id, sample size, residual count, reviewer.

## Images of documents
Mask stamps/signatures with names, header blocks, barcodes/QR codes; check margins and handwritten notes.

## DICOM (v2, with imaging engineer)
DICOM PS3.15 Basic Application Confidentiality Profile: remove/replace identifying attributes, remap UIDs consistently, remove private tags unless whitelisted, shift or truncate dates per policy, OCR check for burned-in text, check for facial reconstruction risk in head CT. Use the imaging skill's `dicom_deid_check.py`.
