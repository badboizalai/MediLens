# synth_gen

Deterministic, 100 % synthetic medical-record generator for golden-v0 (`ml/eval/golden-v0`).

    uv run --with pillow python -m synth_gen.generate --out ../../eval/golden-v0

Requirements: the **DejaVu Sans** font (Vietnamese diacritics) installed on the system
(e.g. `apt install fonts-dejavu-core`). Handwriting is simulated from DejaVu Sans with
per-glyph jitter/rotation/stroke width (no handwriting font is bundled or downloaded).
Image variants: `clean`, `degraded` (blur/skew/shadow/fold), and for a seeded ~20 % of
records `handwriting` or `perspective` (4-point warp). Ground truth is unaffected.

Profiles: `--profile v0` (default, golden-v0, 50 docs) or `--profile v1` (golden-v1, 150 docs, seed 20261001, adds `region`; schemas in `ml/schemas`).

`synth_gen.pages` (S6-T54c): text-level 9-type page set for the classifier, 40 pages per type split dev/test; see `DATASET_CARD.md`.
