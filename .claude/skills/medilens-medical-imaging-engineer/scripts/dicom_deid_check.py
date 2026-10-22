#!/usr/bin/env python3
"""Check DICOM files for identifying data left after de-identification.

Usage: python dicom_deid_check.py <file-or-folder> [--max-files 500]

Reports, per file, non-empty identifying attributes (PS3.15 basic list used
by MediLens), private tags, BurnedInAnnotation = YES, and whether
PatientIdentityRemoved = YES. Never prints attribute values (only names).
Exit 1 if any file fails. Requires pydicom.
"""
import os
import sys

try:
    import pydicom
except ImportError:  # pragma: no cover
    print("pydicom is required: pip install pydicom")
    sys.exit(2)

IDENTIFYING = [
    "PatientName", "PatientID", "PatientBirthDate", "OtherPatientIDs", "OtherPatientNames",
    "PatientAddress", "PatientTelephoneNumbers", "PatientMotherBirthName", "ReferringPhysicianName",
    "PerformingPhysicianName", "OperatorsName", "InstitutionName", "InstitutionAddress", "StationName",
    "AccessionNumber", "StudyID", "DeviceSerialNumber", "RequestingPhysician", "AdditionalPatientHistory",
    "PhysiciansOfRecord", "NameOfPhysiciansReadingStudy", "MedicalRecordLocator", "PatientInsurancePlanCodeSequence",
]


def check_file(path):
    problems = []
    try:
        ds = pydicom.dcmread(path, stop_before_pixels=True, force=True)
    except Exception as exc:  # noqa: BLE001
        return [f"unreadable ({type(exc).__name__})"]
    for kw in IDENTIFYING:
        if kw in ds:
            val = ds.get(kw)
            if val not in (None, "", [], b"") and str(val).strip() not in ("", "ANONYMIZED", "ANONYMOUS"):
                problems.append(f"identifying attribute present: {kw}")
    private = [el.tag for el in ds.iterall() if el.tag.is_private]
    if private:
        problems.append(f"{len(private)} private tag(s) present")
    if str(ds.get("BurnedInAnnotation", "")).upper() == "YES":
        problems.append("BurnedInAnnotation = YES (mask or reject pixels)")
    if str(ds.get("PatientIdentityRemoved", "")).upper() != "YES":
        problems.append("PatientIdentityRemoved is not YES")
    return problems


def iter_files(target, limit):
    if os.path.isfile(target):
        yield target
        return
    count = 0
    for root, _d, files in os.walk(target):
        for f in sorted(files):
            yield os.path.join(root, f)
            count += 1
            if count >= limit:
                return


def main(argv):
    args = argv[1:]
    if not args:
        print(__doc__)
        return 2
    limit = 500
    if "--max-files" in args:
        limit = int(args[args.index("--max-files") + 1])
    target = args[0]
    checked = failed = 0
    for path in iter_files(target, limit):
        checked += 1
        probs = check_file(path)
        if probs:
            failed += 1
            print(f"FAIL {os.path.relpath(path, target if os.path.isdir(target) else os.path.dirname(target) or '.')}")
            for p in probs:
                print("     -", p)
    print(f"checked={checked} failed={failed} → {'FAIL' if failed else 'PASS'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
