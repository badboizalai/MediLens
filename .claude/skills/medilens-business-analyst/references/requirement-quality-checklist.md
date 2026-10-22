# Requirement Quality Checklist

Run before handing any requirement artefact to design, development or QA.

## Each requirement / story
- [ ] Single behaviour; no "and/or" bundling of unrelated behaviours
- [ ] Uses MUST/SHOULD/MAY deliberately
- [ ] Measurable: numbers for time, size, count, percentage
- [ ] Persona and Unit named
- [ ] Data touched and its class (C4/C3/C2/C1) stated
- [ ] Linked BR / SEC / NFR codes
- [ ] Acceptance criteria in Gherkin: happy path + boundaries + permission denial + errors
- [ ] Abuse case present if access or data involved
- [ ] Low-confidence AI behaviour specified (if AI output shown)
- [ ] Accessibility expectation stated (if UI)
- [ ] Out-of-scope lines written
- [ ] No diagnosis / dosing / prognosis behaviour
- [ ] Glossary updated for new terms
- [ ] Estimable and ≤ 3 days, else split

## Ambiguity words to replace
fast, quick, user-friendly, easy, intuitive, secure, robust, many, few, appropriate, as needed, etc., and/or, support (without saying how), handle (without saying how).

## Document level
- [ ] Every FR has a source and rationale
- [ ] Every BR traceable to ≥ 1 story and ≥ 1 test
- [ ] Conflicts with existing BR checked
- [ ] Open questions listed with owner
- [ ] Version, date, change log updated
