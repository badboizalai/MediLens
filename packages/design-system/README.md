# @medilens/design-system

Design tokens (`tokens.json`) and base React components: `Button`, `Card`, `SeverityBadge`, `Alert`, `Dropzone`.

## Tokens
- `cssVariables()` returns CSS custom properties (`--ml-*`); light by default, dark under `[data-theme="dark"]`. Inject it once in the app root.
- Import `src/styles.css` for component styles.
- Tailwind preset: `presets: [require("@medilens/design-system/tailwind-preset")]` (all values map to the CSS variables).

## Severity (BR-020)
`SeverityBadge` always pairs a glyph with a text label (VI/EN); colour is never the only signal. The badge tints the border/glyph and keeps body text at the normal text colour for contrast.

## Dev
`pnpm --filter @medilens/design-system test` (Vitest + Testing Library + vitest-axe) · `storybook` · `build-storybook`.

Consumers (e.g. `apps/web`) integrate separately. Illustrative UI only; no diagnosis wording (BR-042).
