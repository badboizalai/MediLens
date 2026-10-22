# Healthcare UX Principles for MediLens

## Principles
1. **Calm before detail** — summary first, details on demand (progressive disclosure).
2. **Record, meaning, action** — what the record says → what it usually means → what to ask the doctor.
3. **Show the source** — every finding links to the highlighted region of the original document.
4. **Uncertainty is visible** — low-confidence fields are highlighted; unmapped findings listed, never placed on the body by guess.
5. **The user is in control** — confirm before display; easy edit; easy delete; clear sharing scope and expiry.
6. **Never alarm, never minimise** — neutral language, no red full-screen warnings except emergencies.
7. **Inclusive by default** — WCAG 2.2 AA, colour-blind safe, large tap targets, works one-handed on phone.
8. **Privacy is felt** — explain why each permission/data is needed at the moment it is asked.

## Emotional design for serious topics
- Cancer/metastasis screens open with: "Hồ sơ của bạn có ghi nhận… Đây là hình minh họa để bạn dễ trao đổi với bác sĩ."
- Avoid realistic gore; use stylised, soft anatomy; muted background; severity tint at 60–80% opacity.
- Offer "Chỉ xem tóm tắt" mode and a clear way out (back to dashboard).
- Provide support resources link (patient associations, hotline) without pushing.

## Anti-patterns (do not ship)
- Colour-only severity; red pulsing animations.
- Showing survival statistics or prognosis.
- Auto-playing 3D rotation or sound.
- Hiding the disclaimer in a footer only.
- Asking for consent with pre-ticked boxes.
- Dark patterns around sharing (default "share everything forever").
- Medical jargon without tooltip.

## Trust signals
- Source badges (WHO, Bộ Y tế, MedlinePlus) on explanations.
- "Reviewed on <date>" on articles.
- "AI-generated, please verify" label on extraction results.
- Visible security cues: MFA prompt, active sessions list, audit of who viewed shared data.
