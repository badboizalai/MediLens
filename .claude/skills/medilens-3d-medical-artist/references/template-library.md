# Template library (plan section 27)

## Templates
| Template | Use | Notes |
| --- | --- | --- |
| adult_male | default when sex recorded male | |
| adult_female | default when sex recorded female | breast, uterus, ovaries regions |
| child_6_12 | caregiver-managed child profiles | proportions differ; paediatric caution banner |
| neutral | sex not recorded | regions common to both; sex-specific regions shown on demand |
Same region codes across templates; template-specific regions documented in the region tree.

## Scaling
Viewer applies non-uniform scale from height and weight bands (no baked variants); organs keep relative position.

## organ_status
present (normal) · removed (hidden or ghosted 15% opacity with label "removed, per record") · absent_congenital (hidden + label) · transplanted (shown with badge) · implant_present (device glyph attached to the region). Values match `organ_status` in the data model (plan 27.4).

## Devices (glyph library)
coronary stent · pacemaker/ICD · prosthetic valve · joint replacement (hip/knee) · spinal hardware · dental implant · breast implant · IUD · cochlear implant. Each: simple, low-poly, distinctive silhouette, neutral colour, label on hover.

## Variants
situs inversus, single kidney, horseshoe kidney, accessory spleen: v1 shows a notice and organ-level highlight; mirrored/variant meshes only after CSO approval.
