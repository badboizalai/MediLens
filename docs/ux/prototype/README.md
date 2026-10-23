# Clickable low-fidelity prototype [S2-F07]

Static prototype of the 8 MVP screens for the 3-person usability test (D14). Plain HTML/CSS/JS, no build step, no backend, no network calls, no storage. All data is fictional and synthetic ("Nguyen Van Mau", a made-up dental record).

## How to open
Double-click `index.html`, or open it in a browser by file path (`file://`). Works offline. Reload (or the "Reset" button in Settings) returns to the start state.

## Screens (hash routes)
`#consent` -> `#upload` -> `#review` -> `#viewer` -> `#explain` -> `#timeline` -> `#share` -> `#settings`

- Main flow: tick the required consent box, choose the sample record, tick "I checked this item" on the two flagged fields, then "Confirm and show on the body".
- Viewer: inline SVG tooth chart (FDI style). Element ids follow `region_code` style (`tooth-36`, `tooth-46`, `tooth-24`). Severity uses the design-system token colours plus a glyph and a text label, so it is never colour only. Click or press Enter on a tooth, or use the list.
- Explain: canned answers only (no model). Dose and outlook questions show the refusal copy.
- Language: VI default, EN toggle top right. Copy comes from `docs/ux/wireframes/*.md`; a few labels are prototype-only.
- Keyboard: Tab through everything, visible focus ring, skip link, 44 px targets, `prefers-reduced-motion` respected, light/dark by system setting.

## Not in scope
Real upload, OCR, 3D, accounts, persistence. Timeline compares two fixed visits. This is an illustration tool prototype; it contains no medical conclusions.

## Test tasks (from `docs/ux/usability-test-script.md`)
Run in Vietnamese, think-aloud, about 30 min. Start at the Consent screen. Facilitator does not explain the UI.

| # | Task (VI / EN) | Screens | Success | Max |
| --- | --- | --- | --- | --- |
| T1 (main) | "Hãy tải hồ sơ nha khoa này lên và xác nhận kết quả." / "Upload this dental record and confirm the results." | Consent, Upload, Review, Viewer | Agrees to consent, uploads, confirms all flagged fields, reaches Viewer with confirmed findings | 5 min |
| T2 | "Tìm xem răng nào có vấn đề và điều đó có nghĩa là gì." / "Find which tooth has a problem and what it means." | Viewer, Explain | Names tooth 36 and "sâu răng" (per record) and finds the illustration notice | 2 min |
| T3 | "Chia sẻ hồ sơ nha khoa với bác sĩ trong 7 ngày." / "Share the dental record with a doctor for 7 days." | Share | Share created with Dental scope and 7-day expiry | 3 min |

Comprehension questions, SUS, pass criteria and the recording sheet are in the script. Between participants, press "Reset" in Settings.

## Checks
```
python3 .claude/skills/medilens-regulatory-privacy-officer/scripts/claims_lint.py docs/ux
```
