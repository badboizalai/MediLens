# Lab normalisation

1. Identify the test name as written (VI/EN/abbreviation) → candidate LOINC codes (component, property, system, scale).
2. Choose the LOINC code only when specimen and property are clear (e.g., creatinine in serum/plasma, mass/volume); otherwise leave uncoded with the original name.
3. Value: keep the number and comparator (<, >, ≤) exactly; keep the unit string as written; map to a UCUM code when unambiguous (mg/dL, µmol/L, mmol/L, %, mL/min/1.73m2).
4. Conversion: only show converted values when the conversion factor is fixed and documented; always keep the original.
5. Reference range: copy the range printed on the record; if absent, show none. Never use population ranges to judge.
6. Flag: "outside the range printed on your record" (neutral wording); no severity colour from lab flags alone.
7. Dates: collection date from the record; if only report date is present, mark it as such.

Examples
| Record text | LOINC | UCUM |
| --- | --- | --- |
| Creatinin máu 1.2 mg/dL | 2160-0 Creatinine [Mass/volume] in Serum or Plasma | mg/dL |
| eGFR 58 | 33914-3 (eGFR, MDRD) — or the specific equation code if the record states CKD-EPI | mL/min/{1.73_m2} |
| HbA1c 7.1 % | 4548-4 Hemoglobin A1c/Hemoglobin.total in Blood | % |
Codes above must be re-checked against the current LOINC release before loading.
