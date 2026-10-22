# DICOM intake

1. Upload: multipart to the quarantine bucket; limits from config (default ≤ 1 GB ZIP, ≤ 3,000 files).
2. Scan: GuardDuty Malware Protection result must be clean.
3. Safe unzip in the worker sandbox (no network): reject absolute paths and `..`, compression ratio > 100:1, nested archives, symlinks; stop at size/file limits.
4. Parse: accept files with the DICM preamble (Part 10) or valid implicit-VR files; skip DICOMDIR and non-image objects; never trust file extensions.
5. Filter: Modality = CT (v2); ignore SR/SEG/RTSTRUCT for now (log types only).
6. Group by SeriesInstanceUID; choose the series with ImageOrientationPatient ≈ axial, most instances, thinnest SliceThickness; let the user pick if two candidates tie.
7. Sort by projection of ImagePositionPatient on the slice normal (not by InstanceNumber); check spacing consistency (gaps > 1.5× median → warn).
8. Convert to NIfTI (orientation preserved, Hounsfield units via RescaleSlope/Intercept) for segmentation.
9. Record: number of series/instances, chosen series (remapped UID), spacing, dimensions — no identifiers.
