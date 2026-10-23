# Normaliser eval (S7-T62, D62)

`to_loinc` on `ml/eval/normalise/synthetic_labs.csv` (own-authored synthetic strings; VI/EN names, values and units in text or separate, typos, and strings that must be refused). ICD-10 is not evaluated: LIC-002 is not approved and no ICD-10 code is loaded.

- Strings: **175** (153 with a gold LOINC code, 22 that must be refused)
- **Top-1 code accuracy: 0.908** (139/153), target >= 0.85 -> PASS
- Precision when answered: 1.000 (139/139)
- Refusal accuracy on negatives: 22/22
- Outcomes: correct 139, correct refusal 22, missed (abstained) 14

## Errors

| text | unit | gold | got | class |
|---|---|---|---|---|
| HbAlc 6.0 % |  | 4548-4 |  | missed (abstained) |
| Blood sugar | mg/dL | 2345-7 |  | missed (abstained) |
| Serum glucose | mg/dL | 2345-7 |  | missed (abstained) |
| Creatinine huyết thanh | mg/dL | 2160-0 |  | missed (abstained) |
| Men gan ALT | U/L | 1742-6 |  | missed (abstained) |
| Hemoglobin glycosyl hóa | % | 4548-4 |  | missed (abstained) |
| Cholesterol xấu (LDL) | mg/dL | 13457-7 |  | missed (abstained) |
| Cholesterol tốt (HDL) | mg/dL | 2085-9 |  | missed (abstained) |
| Mỡ máu triglycerid | mg/dL | 2571-8 |  | missed (abstained) |
| Ure máu | mg/dL | 3094-0 |  | missed (abstained) |
| Left ventricular EF | % | 10230-1 |  | missed (abstained) |
| Oxy máu SpO2 97 % |  | 59408-5 |  | missed (abstained) |
| Nhịp tim lúc nghỉ 70 bpm |  | 8867-4 |  | missed (abstained) |
| Gluco 5.0 mmol/L |  | 15074-8 |  | missed (abstained) |

## Notes

Reading (numbers above come from the run that produced this file; re-run the script to refresh them):

- The first 155 strings were written against the dictionary's vocabulary (in-vocabulary slice: 136/137 correct, 0.993). The last 20 rows are an out-of-vocabulary slice (paraphrases, unseen VI wording): 3/16 correct. The 0.908 headline mixes both, so treat it as optimistic for real OCR text.
- Every miss is "missed (abstained)"; there is no wrong-code answer. Top error classes:
  1. Unlisted VI/EN paraphrase of a listed analyte (Blood sugar, Serum glucose, Ure máu, Creatinine huyết thanh, Men gan ALT, cholesterol xấu/tốt, Left ventricular EF, Nhịp tim lúc nghỉ, Oxy máu SpO2). Fix: add aliases from real, de-identified report vocabulary.
  2. Extra words around a known name change the token count, so fuzzy matching is off by design (guard against partial matches).
  3. OCR digit/letter confusion in a code-like name (HbAlc for HbA1c) and truncation (Gluco) score about 0.80-0.83, below the 0.85 cut-off.
- One false accept appeared during development ("Troponin hs" matched Troponin T through a swapped token). Fixed by requiring every differing token pair to be a near-match, with a unit test. The set shows 0 false accepts, but it has only 22 refusal strings, so this is not a safety estimate.
- Analytes with two units (glucose, lipids, creatinine) and troponin without a type abstain when no unit decides, by design.
- Abbreviation expansion is covered by unit tests, not by this accuracy number.
