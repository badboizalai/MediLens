# Asset standards

| Item | Rule |
| --- | --- |
| Format | glTF 2.0 binary (.glb) |
| Units / axes | metres, Y-up, right-handed, origin at body midline between feet (body) or organ centroid (organ files) |
| Naming | node/mesh name = region_code; parents = organ/system codes; `aux_` for helpers; `device_<type>_<n>` |
| Materials | PBR metallic-roughness, single neutral base material per system; no textures unless approved |
| Budgets | default body view ≤ 5 MB (compressed); body shell ≤ 30k triangles; large organ ≤ 20k; small structure ≤ 5k; tooth ≤ 1.5k |
| Compression | Draco or meshopt; quantised attributes |
| LOD | LOD0 (detail view), LOD1 (overview ≈ 30–50% triangles) |
| Normals | outward, smooth shading with angle threshold; no non-manifold edges in organs |
| Transparency | skin/shell as separate mesh to allow alpha fade |
| Metadata | `extras.region_code`, `extras.source`, `extras.licence`, `extras.version` |
| Files | `packages/anatomy-assets/<unit>/<name>@<version>.glb` + preview PNG + source .blend in LFS |
