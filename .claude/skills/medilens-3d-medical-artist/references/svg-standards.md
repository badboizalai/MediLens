# SVG standards (2D body maps, organ diagrams, odontogram)

- One file per view: `body_front.svg`, `body_back.svg`, `<organ>.svg`, `odontogram.svg`.
- `viewBox` fixed; no width/height attributes (responsive).
- `id` = region_code for each clickable path; tooth surfaces `tooth_36_O|M|D|B|L`; groups per system `<g id="sys_respiratory">`.
- No inline fill colours on region paths (the viewer sets fill from tokens); outlines via a class.
- Every region has `<title>` with VI name for accessibility, or the viewer supplies aria labels from the region list.
- No scripts, no external references, no embedded raster images.
- Check with `svg_region_check.py`.
