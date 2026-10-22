# CT test cases
| ID | Case | Expected |
| --- | --- | --- |
| CT-01 | Clean public chest/abdomen CT | Meshes for listed organs, TRE < 15 mm |
| CT-02 | ZIP with path traversal entry | Rejected, nothing extracted |
| CT-03 | Zip bomb (ratio > 100:1) | Rejected |
| CT-04 | Mixed modalities (CT + SR) | Only CT used; SR ignored and logged by type |
| CT-05 | Two axial series | Thinnest/most slices chosen or user prompted |
| CT-06 | Burned-in annotation = YES | Masked or rejected |
| CT-07 | Private tags present | Removed |
| CT-08 | Missing slices (gap) | Warning; meshing continues with notice |
| CT-09 | Partial field of view (no kidneys) | "Not in field of view" note; template parts ghosted |
| CT-10 | Post-nephrectomy | organ_status = removed respected; no fake kidney |
| CT-11 | Head CT | Excluded in v2 (face risk) |
| CT-12 | 1.2 GB ZIP | Rejected by size limit |
