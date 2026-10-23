# anatomy-assets
GLB/SVG/unit configs. Mesh/element names MUST equal `region_code`. Validate with `.claude/skills/medilens-frontend-engineer/scripts/check_glb_regions.py`. Owner: `medilens-3d-medical-artist`.

## 2D body map (`svg/body-front.svg`, `svg/body-back.svg`)
- Element `id` = `region_code` from `data/terminology/region-tree.v1.yaml`; each region is `class="region"` with a `<title>` holding an i18n key (`anatomy.region.<region_code>`). No inline fill: the viewer colours via CSS (`currentColor` strokes). Silhouette/group ids use the `aux_` prefix. Patient's right is on the viewer's left in the front view, and mirrored in the back view.
- Drawn: organ, bone-site and lymph-node regions (41 distinct region codes across both files). Not drawn: cardiac sub-structures, coronaries, great vessels (heart viewer), dental jaws/quadrants/teeth (FDI chart), and group nodes.
- Check: `uv run pytest tests/assets -s` (runs in `make test`) (prints undrawn regions).
- Attribution: original artwork drawn for MediLens from simple geometric shapes; no external source, nothing to attribute (released under the repository licence).

## Odontogram (`svg/odontogram.svg`)
- 32 permanent teeth, FDI layout, clinician view: patient's right on the viewer's left; upper arch (18..11 | 21..28) above, lower arch (48..41 | 31..38) below, gap at the midline. Deciduous teeth (51-85) are not drawn.
- Tooth = `<g id="tooth_NN" class="tooth">` (id = `region_code`, with `<title>` and FDI `<text>` label). Surfaces are child shapes `id="tooth_NN__{M|D|O|B|L}"`, `class="surface surface-X"`; M/D swap sides by quadrant (mesial faces the midline), B on top, L at the bottom, O in the centre. Surface ids are viewer-level, not region_codes.
- No states baked in (no fill). The viewer applies them via CSS; expected hooks: `.tooth[data-state="caries|filled|missing|implant"]`, `.surface[data-state=...]`, `.surface.is-selected`. Strokes use `currentColor`.
- Check: `uv run --with pyyaml pytest -q tests/assets`.
- Attribution: original artwork drawn for MediLens from simple geometric shapes; nothing to attribute.

## Unit configs (`units/`)
- `dental.yaml`, `cardiology.yaml` validate against `units/unit-config.schema.json`; they are the `config` jsonb of `clinical.unit_configs`. Adding a Unit = add a YAML (+ extraction schema), no core code (PB-02).
- `regions` must exist in `data/terminology/region-tree.v1.yaml`; `observations[].loinc` must exist in `data/terminology/loinc-cardiology.v1.csv` with the same UCUM unit.
- `visual_rules` only map severity to design-system tokens (no wording; BR-042). No ICD-10 codes (LIC-002 pending).
- Check: `uv run --with pyyaml --with jsonschema pytest -q tests/assets/test_unit_configs.py`.
