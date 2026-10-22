# Registration to the template

Goal: put patient meshes in the template coordinate frame so regions, camera presets and the comparison mode work.
1. Landmarks (≥ 6): e.g., vertebral bodies T1/L1/L5 centroids, carina, liver dome, kidney centroids, femoral heads — computed from masks.
2. Rigid (rotation + translation) by least squares on landmarks → affine (scaling for body size) → optional thin-plate spline for organ-level fit.
3. Error: target registration error on held-out landmarks; report mean, median, max; gate: mean < 15 mm (plan 27.3).
4. Fallback: if error exceeds the gate or landmarks are missing, show the template with organ-level highlights and a notice.
5. Store the transform and its error with the mesh; recompute when templates change.
