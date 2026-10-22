# DICOM de-identification (PS3.15 Basic Application Confidentiality Profile — summary)

Always apply the current standard's attribute table; the list below is the minimum checked by `dicom_deid_check.py`.

| Action | Attributes (examples) |
| --- | --- |
| Remove or empty | PatientName (0010,0010), PatientID (0010,0020), PatientBirthDate (0010,0030) [or keep year per policy], OtherPatientIDs (0010,1000), PatientAddress (0010,1040), PatientTelephoneNumbers (0010,2154), PatientMotherBirthName (0010,1060), MilitaryRank, EthnicGroup (0010,2160) per policy, ReferringPhysicianName (0008,0090), PerformingPhysicianName (0008,1050), OperatorsName (0008,1070), InstitutionName (0008,0080), InstitutionAddress (0008,0081), StationName (0008,1010), AccessionNumber (0008,0050), StudyID (0020,0010), DeviceSerialNumber (0018,1000), RequestingPhysician (0032,1032), AdditionalPatientHistory (0010,21B0) |
| Replace consistently | StudyInstanceUID, SeriesInstanceUID, SOPInstanceUID, FrameOfReferenceUID (new UIDs under the project root, mapping kept only inside the PHI Service) |
| Dates/times | StudyDate, SeriesDate, AcquisitionDate, ContentDate: shift by a per-user random offset or keep year/month per policy; keep intervals consistent |
| Private tags | Remove all unless whitelisted after review |
| Flags | PatientIdentityRemoved (0012,0062) = YES; DeidentificationMethod (0012,0063) describes the profile/options |
| Pixel data | If BurnedInAnnotation (0028,0301) = YES or OCR finds text → mask regions or reject the series |
| Faces | Head CT can allow facial reconstruction; v2 excludes head series or applies defacing before meshing |
