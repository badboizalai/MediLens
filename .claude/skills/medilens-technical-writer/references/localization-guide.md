# Localization guide

- Library: next-intl with ICU MessageFormat; files `messages/vi.json`, `messages/en.json` (nested keys by screen).
- Keys: `screen.section.purpose` (e.g., `upload.error.blurry`), never reuse a key for different meaning.
- Placeholders: `{name}`, `{count, plural, one {# tài liệu} other {# tài liệu}}` — identical variable names in both languages.
- Glossary: approved term per concept (VI, EN, definition, do-not-use variants); medical terms synced with the BA/AI glossary; CSO approves medical entries.
- Process: author in VI (primary) → translate EN → second-person review → CSO review for medical strings → `i18n_check.py` in CI → screenshot review on both locales.
- Length: EN is often shorter than VI; design for +30% text length; no text in images.
- Locale formatting via Intl APIs (dates, numbers); never hand-format.
