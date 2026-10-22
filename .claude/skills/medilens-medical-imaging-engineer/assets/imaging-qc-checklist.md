# Imaging QC checklist — case <id>
- [ ] Intake: series chosen, spacing consistent, no unexpected modalities
- [ ] De-identification: dicom_deid_check PASS; burned-in text check done
- [ ] Segmentation: expected structures present or noted out of field of view; volumes plausible
- [ ] Label map: label_map_check PASS
- [ ] Mesh: budget met; names = region_code; no inverted normals
- [ ] Registration: mean TRE < 15 mm (value: ___)
- [ ] Viewer: watermark present; measurement tools disabled
- [ ] Performance: default view load < 5 s on throttled 4G
- [ ] CSO display review (if new structures)
