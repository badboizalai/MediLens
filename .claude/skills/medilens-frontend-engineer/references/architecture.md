# Frontend Architecture

```
apps/web/src/
├── app/[locale]/(public)|(auth)|(app)/…      routes (App Router)
├── app/api/auth/*                              route handlers: OIDC callback, session cookie, CSRF
├── features/<domain>/                          documents, review, viewer, timeline, explain, sharing, settings, admin
│   └── viewer/core | units/<unit> | registry.ts
├── components/ui/                              Design System (shadcn-based), no business logic
├── lib/api/                                    generated client (openapi-typescript + openapi-fetch) + query hooks
├── lib/auth/                                   session helpers, guards
├── lib/i18n/                                   next-intl config, messages/vi.json, messages/en.json
└── styles/tokens.css                           generated from design-tokens.json
```

## Data flow
Server state: TanStack Query (keys `['documents', id]`, `['findings', {unit, from, to}]`); mutations invalidate keys; optimistic updates only for non-critical UI (never for confirm). UI state: Zustand stores per feature (viewer camera, selected region, layers). Forms: React Hook Form + Zod schemas generated/derived from OpenAPI types.

## Auth
OIDC Authorization Code + PKCE handled server-side in route handlers; session stored in encrypted HttpOnly cookie; API calls go through same-origin `/api/proxy/*` (BFF) or with cookie-auth to API domain; refresh handled server-side. Client never sees refresh tokens.

## Realtime
`useDocumentEvents(id)` wraps EventSource with reconnect/backoff and falls back to polling every 5 s; updates query cache.

## Error handling
Problem Details → typed error → `ErrorState` component with `title` and retry; 401 → redirect to sign-in preserving return URL; 404 → not found page (never reveal existence).

## Routing guards
`(app)` layout checks session + consent (BR-002) → redirect to `/onboarding/consent` if missing.
