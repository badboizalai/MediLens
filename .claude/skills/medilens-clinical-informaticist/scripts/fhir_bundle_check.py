#!/usr/bin/env python3
"""Check a FHIR R4 Bundle (or a CSV of codes) for MediLens import.

Usage:
  python fhir_bundle_check.py bundle.json
  python fhir_bundle_check.py --codes mapping.csv     (columns: target_system, code)

Bundle checks: resourceType/type, resource types supported or ignored, references
resolve inside the bundle, Condition/Observation codings use known systems with
valid formats (ICD-10 pattern, LOINC check digit, UCUM present for quantities),
dates parse, and identity fields that must be dropped at the PHI boundary.
Exit 1 on errors (warnings do not fail).
"""
import csv
import json
import re
import sys
from datetime import date

SUPPORTED = {"Patient", "Condition", "Observation", "Procedure", "DocumentReference",
             "Encounter", "BodyStructure", "Device", "DeviceUseStatement", "ImagingStudy"}
IGNORED = {"MedicationStatement", "MedicationRequest", "AllergyIntolerance", "Immunization",
           "Practitioner", "Organization", "Composition", "DiagnosticReport"}
ICD10_SYS = "http://hl7.org/fhir/sid/icd-10"
LOINC_SYS = "http://loinc.org"
UCUM_SYS = "http://unitsofmeasure.org"
ICD10_RX = re.compile(r"^[A-Z][0-9]{2}(\.[0-9A-Z]{1,2})?$")
LOINC_RX = re.compile(r"^(\d{1,5})-(\d)$")
IDENTITY_FIELDS = ("name", "identifier", "telecom", "address", "photo", "contact")
FDI = {f"{q}{t}" for q in (1, 2, 3, 4) for t in range(1, 9)} | {f"{q}{t}" for q in (5, 6, 7, 8) for t in range(1, 6)}


def luhn_check_digit(payload: str) -> int:
    total = 0
    for i, ch in enumerate(reversed(payload)):
        d = int(ch)
        if i % 2 == 0:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return (10 - total % 10) % 10


def check_code(system: str, code: str) -> str | None:
    if system in (ICD10_SYS, "ICD-10"):
        return None if ICD10_RX.match(code or "") else f"ICD-10 code '{code}' has an invalid format"
    if system in (LOINC_SYS, "LOINC"):
        m = LOINC_RX.match(code or "")
        if not m:
            return f"LOINC code '{code}' has an invalid format"
        if luhn_check_digit(m.group(1)) != int(m.group(2)):
            return f"LOINC code '{code}' fails the check digit"
        return None
    if system in ("FDI",):
        return None if code in FDI else f"FDI tooth '{code}' is not a valid permanent/deciduous tooth"
    return None


def parse_date(value: str) -> bool:
    if not isinstance(value, str):
        return False
    try:
        if len(value) == 4:
            int(value)
            return True
        date.fromisoformat(value[:10])
        return True
    except ValueError:
        return False


def check_bundle(path: str) -> int:
    with open(path, encoding="utf-8") as fh:
        b = json.load(fh)
    errors, warns = [], []
    if b.get("resourceType") != "Bundle":
        errors.append("resourceType must be Bundle")
    if b.get("type") not in ("collection", "document", "searchset", "transaction", "batch"):
        errors.append(f"unsupported bundle type {b.get('type')!r}")
    entries = b.get("entry") or []
    ids = {f"{e.get('resource', {}).get('resourceType')}/{e.get('resource', {}).get('id')}" for e in entries}
    counts = {}
    for n, e in enumerate(entries):
        r = e.get("resource") or {}
        rt = r.get("resourceType")
        counts[rt] = counts.get(rt, 0) + 1
        where = f"entry[{n}] {rt}/{r.get('id')}"
        if rt in IGNORED:
            warns.append(f"{where}: not displayed in MediLens (ignored)")
            continue
        if rt not in SUPPORTED:
            warns.append(f"{where}: unknown resource type, ignored")
            continue
        if rt == "Patient":
            present = [f for f in IDENTITY_FIELDS if f in r]
            if present:
                warns.append(f"{where}: identity fields {present} will be dropped at the PHI boundary")
        subj = (r.get("subject") or {}).get("reference")
        if subj and subj not in ids:
            warns.append(f"{where}: subject reference {subj} not found in bundle")
        for coding in (r.get("code") or {}).get("coding", []) or []:
            msg = check_code(coding.get("system"), coding.get("code"))
            if msg:
                errors.append(f"{where}: {msg}")
        if rt == "Condition" and not (r.get("code") or {}).get("coding") and not (r.get("code") or {}).get("text"):
            errors.append(f"{where}: Condition without code or text")
        if rt == "Observation":
            if "valueQuantity" in r:
                q = r["valueQuantity"]
                if "value" not in q:
                    errors.append(f"{where}: valueQuantity without value")
                if not q.get("unit") and not q.get("code"):
                    warns.append(f"{where}: quantity without unit")
                if q.get("system") and q.get("system") != UCUM_SYS:
                    warns.append(f"{where}: unit system is not UCUM")
            if not r.get("referenceRange"):
                warns.append(f"{where}: no reference range (show none; never invent)")
        for key in ("recordedDate", "effectiveDateTime", "performedDateTime", "date", "birthDate"):
            if key in r and not parse_date(r[key]):
                errors.append(f"{where}: {key} is not a valid date ({r[key]!r})")
    print("Resources:", ", ".join(f"{k}={v}" for k, v in sorted(counts.items(), key=lambda kv: str(kv[0]))))
    for w in warns:
        print("WARN ", w)
    for x in errors:
        print("ERROR", x)
    print("RESULT:", "FAIL" if errors else "PASS")
    return 1 if errors else 0


def check_codes_csv(path: str) -> int:
    bad = 0
    with open(path, newline="", encoding="utf-8") as fh:
        for i, row in enumerate(csv.DictReader(fh), 2):
            msg = check_code((row.get("target_system") or "").strip(), (row.get("code") or "").strip())
            if msg:
                bad += 1
                print(f"line {i}: {msg}")
    print("RESULT:", "FAIL" if bad else "PASS")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--codes":
        sys.exit(check_codes_csv(sys.argv[2]))
    if len(sys.argv) == 2:
        sys.exit(check_bundle(sys.argv[1]))
    print(__doc__)
    sys.exit(2)
