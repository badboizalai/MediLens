# Synthetic Medical Record Recipe

## 1. Content generation
- Per Unit, write a YAML "case template": demographics range, conditions with ICD-10, typical observations with ranges, procedures, phrasing variants (formal, abbreviated, mixed VI/EN), common abbreviations.
- Use an LLM to fill templates into record text **with structured ground truth emitted at the same time** (the generator returns both the narrative and the JSON labels).
- Use fake names/addresses from a generator; never real people. Mark every file `synthetic=true`.

## 2. Layout rendering
- HTML templates mimicking Vietnamese forms (header with hospital-like name — fictional, patient block, diagnosis block, tables for labs, signature/stamp area).
- Render with Playwright/Chromium to PDF, then rasterise at 150–300 DPI.
- Fonts: Times New Roman/Arial-like for printed; handwriting fonts supporting Vietnamese diacritics for "handwritten" fields.

## 3. Augmentation (to mimic phone photos)
Rotation ±7°, perspective warp, Gaussian blur σ 0–2, motion blur, JPEG quality 40–90, shadows/gradients, paper folds/creases overlays, low light/noise, partial crop, coloured stamps over text. Keep the bbox labels transformed accordingly.

## 4. Quality mix target
50% good, 35% medium, 15% poor; 20% containing handwritten fields; 10% with two-column or table-heavy layouts.

## 5. Validation of synthetic data
- Human spot-check 5% for realism and label correctness.
- Check distribution matches templates; check diacritics preserved.
- Keep a small set of public/real-like redacted samples (with permission) to measure the synthetic-to-real gap.

## 6. Public resources (check licence and terms before use)
MTSamples (English transcriptions), MIMIC-IV-Note (credentialed access), FUNSD/CORD (layout), ISIC (skin images), public dental panoramic datasets.
