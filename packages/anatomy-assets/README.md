# anatomy-assets
GLB/SVG/unit configs. Mesh/element names MUST equal `region_code`. Validate with `.claude/skills/medilens-frontend-engineer/scripts/check_glb_regions.py`. Owner: `medilens-3d-medical-artist`.

## 2D body map (`svg/body-front.svg`, `svg/body-back.svg`)
- Element `id` = `region_code` from `data/terminology/region-tree.v1.yaml`; each region is `class="region"` with a `<title>` holding an i18n key (`anatomy.region.<region_code>`). No inline fill: the viewer colours via CSS (`currentColor` strokes). Silhouette/group ids use the `aux_` prefix. Patient's right is on the viewer's left in the front view, and mirrored in the back view.
- Drawn: organ, bone-site and lymph-node regions (41 distinct region codes across both files). Not drawn: cardiac sub-structures, coronaries, great vessels (heart viewer), dental jaws/quadrants/teeth (FDI chart), and group nodes.
- Check: `uv run pytest tests/assets -s` (runs in `make test`) (prints undrawn regions).
- Attribution: original artwork drawn for MediLens from simple geometric shapes; no external source, nothing to attribute (released under the repository licence).
