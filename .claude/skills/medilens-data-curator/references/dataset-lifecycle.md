# Dataset lifecycle

## Identity and versions
`DS-<nnn>@v<k>`: immutable folder or S3 prefix with manifest (file list + SHA-256), Dataset Card, licence ids, consent basis, creation script commit, schema version.

## Sizing (evaluation)
n = z² · p(1 − p) / e² with z = 1.96 (95%), expected accuracy p, margin e. p = 0.85, e = 0.05 → n ≈ 196 (use 200) per reported stratum; e = 0.03 → ≈ 545. Report per Unit and per main document type; keep ≥ 30 per subgroup (handwritten/printed, photo quality, VI/EN, adult/child) for bias checks. Use `scripts/sample_size.py`.

## Sizing (training)
Learning curve at 10/25/50/100%: if the metric still rises clearly at 100%, collect more; if flat, stop. Distillation needs roughly 1,000–3,000 confirmed documents per Unit as a starting point.

## Splits and leakage
Split by source document family (same patient/template never in two splits). Golden set is frozen and separate. Run `scripts/leakage_check.py` (SHA-256 of normalised text or file bytes) before each evaluation; any overlap fails.

## Maintenance (plan 25.5)
| Activity | Cadence |
| --- | --- |
| Register each new version | each version |
| License register review | quarterly |
| Golden refresh 10–20% (fixed core kept) | quarterly |
| Drift monitoring (document mix, quality, correction rate) | weekly; > 20% shift → collect data |
| Consent withdrawal handling | on event |
| Relabel on schema change (conversion script + sample check) | on schema change |
| Retention / deletion | per retention matrix |
| Lineage dataset → model | every training or prompt change |
