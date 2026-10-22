# Region coding

## Naming
snake_case, organ first, then side, then part: `lung_r_upper`, `kidney_l`, `heart_lv`, `tooth_36`, `tooth_36_O` (surface). Systems: `sys_cardiovascular`, `sys_respiratory`. Special: `unmapped`.

## Tree and precision
Each region has `parent` (body → thorax → lung_r → lung_r_upper → lung_r_upper_apical); meshes exist only at some levels, the rest is inferred from the tree. Mapping returns `precision` and `mappingConfidence` (plan 27.2):
| precision | Meaning | Viewer |
| --- | --- | --- |
| exact | finest sub-region stated | highlight that sub-region |
| segment | segment/lobe stated (e.g., right upper lobe) | highlight the segment |
| organ | organ stated, part not (e.g., "phổi phải") | highlight whole organ |
| system | only the system stated ("bệnh tim mạch") | faint system area + "approximate location" |
| body_part | only a body part ("ngực", "bụng") | faint body area + "approximate location" |
`mappingConfidence` < 0.6 → `region = unmapped` (BR-015): list item only, never drawn.

## Laterality
left · right · bilateral · midline · unknown. Unknown side for a paired organ → show at organ level of both sides with "không rõ bên / side not stated"; never guess.

## Standard references
`standard_code` stores FMA id (from BodyParts3D naming) or SNOMED body-structure id when licensed. Keep a crosswalk table in the Unit config.

## Special anatomy (plan section 27)
`organ_status` (plan 27.4): present · removed · absent_congenital · transplanted · implant_present; `variant_code` and `device_type` complete it. Devices: pacemaker, stent, valve prosthesis, joint replacement, dental implant, breast implant… as glyphs linked to a region. Variants (e.g., situs inversus) are flagged on the profile and the viewer shows a notice rather than mirroring the model automatically in v1.

## Review
New regions → 3D artist (mesh names), CSO (meaning), FE (`check_glb_regions.py`).
