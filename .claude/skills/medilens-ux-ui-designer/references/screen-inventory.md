# Screen Inventory

| Screen | Route | Primary action | Key states | Notes |
| --- | --- | --- | --- | --- |
| Landing | /[locale] | Sign up | — | SSG, privacy promise |
| Sign up / Sign in / MFA | /auth/* | Continue | errors, lockout (BR-004) | Passkeys preferred |
| Consent | /onboarding/consent | Agree | re-consent on new version | No pre-ticked boxes |
| Dashboard | /app | Upload record | empty (first use), processing, ready | Recent documents, Units with findings |
| Upload | /app/upload | Choose/take photo | quality warning, too large, wrong type | Capture tips inline |
| Processing | /app/documents/[id] | — | queued, OCR, extracting, failed | SSE progress, can leave page |
| Review | /app/documents/[id]/review | Confirm | low-confidence fields, unmapped, duplicate warning | Side-by-side original + fields |
| Body viewer | /app/viewer | Select region | no findings, WebGL fallback | 2D/3D, layers, findings list |
| Unit viewer | /app/viewer/[unit] | Select region | — | Dental, Cardiology, Oncology plugins |
| Finding detail | panel | Ask a question | no article (fallback) | Record quote + meaning + questions + sources |
| Explain chat | panel | Send question | guardrail refusal, emergency | Streaming, citations |
| Timeline | /app/timeline | Compare dates | single encounter | Side-by-side compare |
| Sharing | /app/sharing | Create share | expired, revoked | Scope + expiry selectors |
| Settings | /app/settings | — | sessions, MFA, export, delete account | DSR actions |
| Admin | /admin/* | — | break-glass request | No PHI by default |

## Reusable patterns
SeverityChip · SourceBadge · DisclaimerBar · ConfidenceField · RegionListItem · ProcessingStepper · ShareScopePicker · EmptyState · ErrorState · BottomSheet.
