# CT viewer (v2)

- Library: Cornerstone3D (OHIF optional for a full viewer). Load de-identified series from S3 via signed URLs; no DICOMweb in v2 unless Orthanc is adopted (ADR-020). AWS HealthImaging is not offered in ap-southeast-1.
- Tools enabled: scroll, zoom/pan, window presets (soft tissue W400/L40, lung W1500/L−600, bone W2000/L300), MPR optional.
- Tools disabled: length/area/HU measurement, annotations, AI overlays of lesions (BR-042).
- Labels: "Ảnh CT của bạn — chỉ để minh họa giải phẫu / Your CT — for anatomy illustration only".
- Performance: progressive loading, web workers; mobile shows the 3D mesh and a reduced slice set.
