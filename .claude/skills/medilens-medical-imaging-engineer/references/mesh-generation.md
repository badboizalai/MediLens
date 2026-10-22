# Mesh generation

1. Marching cubes on each mask (scikit-image) with voxel spacing → surface in patient coordinates (mm).
2. Clean: largest component, fill holes, remove tiny islands (< 1 mL).
3. Smooth: Taubin or Laplacian (few iterations to avoid shrinkage).
4. Decimate to budget: e.g., ≤ 20k triangles per large organ, ≤ 5k small structures; whole default view ≤ 5 MB GLB (Draco/meshopt compression).
5. Transform: LPS (DICOM) → glTF right-handed Y-up, metres; apply registration transform (W6) or keep patient space with a camera preset.
6. Name meshes by region_code; add `extras.source = "ct"`, algorithm versions, series reference (remapped UID).
7. Validate with the 3D artist's `glb_budget_check.py` and FE's `check_glb_regions.py`.
