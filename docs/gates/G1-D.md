# Gate G1-D - Data licence: evidence pack (round 1, evaluation and synthetic data)

> Draft prepared by AI (owner skill: medilens-data-curator; reviewers: regulatory-privacy-officer, qc-release-gatekeeper). **Educational, not legal advice. AI does not sign gates.** Version 0.1, 2026-10-23. Task S5-T49.

**Criterion (plan s25.6):** every dataset licensed for its use; Dataset Card complete; checksum and immutable version; no real data without consent; kappa >= 0.8; golden set separate with no leakage; signed by Regulatory & Privacy and the Data Curator.
**Scope of round 1:** only `ml/eval/golden-v0` (50 docs) and `ml/eval/golden-v1` (150 docs), both 100 % synthetic. No model is trained or fine-tuned on them. Round 2 (S22) covers fine-tuning data.

**Readiness: round 1 evidence complete for the synthetic evaluation sets; gate NOT SIGNED.** Human sign-off and the open gaps below remain.

## 1. Checklist
| # | Criterion | Evidence | Status | Gap |
| --- | --- | --- | --- | --- |
| 1 | Every source in the License Register and licensed for its use | Only source used is LIC-001 (own synthetic generator, approved, `training_allowed=yes`, `redistribution_allowed=yes`, `data/license-register.csv`). `license_register_check.py` -> RESULT: PASS (section 3.3) | met (evaluation use) | `reg_cosign` for LIC-001 is empty; LIC-002..013 are `needs-verification` and not used by any dataset here |
| 2 | Dataset Card complete | `ml/eval/golden-v0/DATASET_CARD.md`, `ml/eval/golden-v1/DATASET_CARD.md`; review in section 4 | partially met | Template fields missing (section 4) |
| 3 | Checksum manifest | `ml/eval/manifests/SHA256SUMS.golden-v0` (141 files), `SHA256SUMS.golden-v1` (407 files); `verify_manifests.py` -> OK (section 3.1) | met | Cards do not yet cite the manifest (section 4) |
| 4 | Immutable version | Versions `v0.1.0`, `v1.0.0` in cards; manifests make drift detectable. Git history is the only immutability control | partially met | No release tag or write-protected copy; verify script not yet run in CI |
| 5 | No real data without consent; de-identification sample checked | Cards state 100 % synthetic, fictional names and facility; generator is template-based with no LLM and no real input | met (synthetic) | No de-identification QA needed for synthetic; a human spot-check of 5 % (3 records v0, 8 records v1) is listed in both cards as still to do |
| 6 | Coverage per group | 3 Units x (17/17/16 in v0, 50/50/50 in v1); VI/EN 80/20; quality 50/35/15 % | partially met | Cards themselves state limits: region codes sparse (cardiology, most oncology), 50 per Unit modest for per-field F1 intervals |
| 7 | Labels reach kappa >= 0.8 | Not applicable: labels are generated with the text, no annotators | n/a (synthetic) | Becomes mandatory for any human-labelled or real set (round 2) |
| 8 | Golden set separate, no leakage | `leakage_check.py` results in section 3.2: v0 vs v1, v0 vs synth, v1 vs synth, all overlap 0 | met (v0/v1/synth); training set not yet exists | Re-run against every future training set |
| 9 | Signed by Regulatory & Privacy and Data Curator | Section 6 table is empty | **not met** | Humans only |

Counts: met 4 (rows 1, 3, 5, 8), n/a 1 (row 7), partially met 3 (rows 2, 4, 6), not met 1 (row 9, blocks GO).

## 2. Re-run commands
```
python3 ml/eval/manifests/make_manifests.py          # regenerate manifests (only after an approved dataset change)
python3 ml/eval/manifests/verify_manifests.py        # exit 1 on mismatch, missing or extra file
uv run pytest ml/eval/manifests
python3 .claude/skills/medilens-data-curator/scripts/leakage_check.py <dir_a> <dir_b> [--text]
python3 .claude/skills/medilens-data-curator/scripts/license_register_check.py data/license-register.csv
```
`verify_manifests` is deliberately not wired into the shared Makefile `governance` target; running it in CI is a follow-up (see section 5).

## 3. Results (run 2026-10-23)
### 3.1 Manifest verification
```
$ python3 ml/eval/manifests/verify_manifests.py
golden-v0: OK
golden-v1: OK
```
Manifests cover every file in each dataset directory (`<sha256>  <relative path>`, sha256sum format, sorted). Counts include `DATASET_CARD.md` (v1 card says 406 files vs the 407 now listed, because the card itself was added after its leakage run; harmless, to correct in the card).

### 3.2 Leakage checks
```
$ leakage_check.py ml/eval/golden-v0 ml/eval/golden-v1
ml/eval/golden-v0: 141 files · ml/eval/golden-v1: 407 files · overlap: 0
RESULT: PASS
$ leakage_check.py ml/eval/golden-v0 ml/eval/golden-v1 --text
ml/eval/golden-v0: 141 files · ml/eval/golden-v1: 407 files · overlap: 0
RESULT: PASS
$ leakage_check.py ml/eval/golden-v0 ml/datasets/synth --text
ml/eval/golden-v0: 141 files · ml/datasets/synth: 9 files · overlap: 0
RESULT: PASS
$ leakage_check.py ml/eval/golden-v1 ml/datasets/synth --text
ml/eval/golden-v1: 407 files · ml/datasets/synth: 9 files · overlap: 0
RESULT: PASS
```
Note: `ml/datasets/synth` holds the generator code and tests only (9 tracked files), no data fixtures, so that comparison is trivially clean. The check is a hash (exact and whitespace-normalised) check; it does not detect near-duplicates. Both goldens share generator templates by design (v1 cards: same content, different seed), so semantic overlap of template phrasing is expected and not measured.

### 3.3 Licence register
```
$ license_register_check.py data/license-register.csv
Sources: 13  mode: learning  today: 2026-10-23
WARN ... (LIC-002..LIC-013: unclear terms; not used by these datasets)
RESULT: PASS
```
Both Dataset Cards declare "Own work (MediLens project)", which corresponds to LIC-001 only. No third-party data, templates or fonts beyond DejaVu Sans rendering (font licence not recorded in the register; see gaps).

## 4. Dataset Card review against `medilens-data-curator/assets/dataset-card-template.md`
| Template field | golden-v0 | golden-v1 |
| --- | --- | --- |
| Name / purpose | present | present |
| Tier (1-4) and sources (LIC ids) | missing Tier; says "Own work", no `LIC-001` id | same |
| Consent basis | missing (implied "own") | same |
| Size, splits, strata counts | present; no split statement (all golden) | present |
| Label schema version, guideline version | schemas in `schemas/*.v1.json`; guideline "none" stated | schemas `ml/schemas/*.v1.json`; guideline "none" stated |
| Annotators, agreement (kappa) | "n/a" stated | "n/a" stated |
| De-identification method and QA result | not stated (synthetic only) | not stated |
| Known gaps and biases | present | present |
| Allowed uses / prohibited uses | present | present |
| Checksum manifest | missing (now exists) | missing (now exists) |
| Created by / date / script commit | date and generator version; no commit hash | same |
| Models using this version | missing | missing |
| Retention / deletion date | missing | missing |

Further gaps: v0 card has no leakage statement; v1 file count (406) is stale; human 5 % spot-check pending in both. Cards were not edited in this PR (out of declared paths); gaps go to the ai-ml-engineer / data-curator as a follow-up.

## 5. What remains before GO (exact list)
1. Human REG co-signs LIC-001 (`reg_cosign` column) and the data-curator confirms the DejaVu Sans font licence for rendered output.
2. Update both Dataset Cards: Tier, `LIC-001`, consent basis, de-identification statement, checksum manifest reference, script commit, models using, retention; fix v1 file count.
3. Complete the 5 % human spot-check (3 + 8 records).
4. Run `verify_manifests.py` in CI (Makefile/workflow change by its owner) and tag the dataset versions.
5. Round 2 (S22): kappa, real/donated data, licences LIC-002..013, leakage vs the actual training set.
6. Human sign-off in section 6.

## 6. Sign-off (humans only)
| Role | Name | Decision (GO / NO-GO / GO with conditions) | Conditions | Signature | Date |
| --- | --- | --- | --- | --- | --- |
| REG (regulatory-privacy-officer, human) | | | | | |
| Data Curator (human) | | | | | |
| QC (evidence check) | | | | | |

## 7. Version history
| Version | Date | Author | Note |
| --- | --- | --- | --- |
| 0.1 | 2026-10-23 | AI (data-curator), S5-T49 | Round 1 evidence pack; unsigned |
