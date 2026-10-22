# Accessibility Checklist (WCAG 2.2 AA, MediLens)

## Perceivable
- [ ] Text contrast ≥ 4.5:1 (large text ≥ 3:1); UI components/graphics ≥ 3:1
- [ ] Severity never conveyed by colour alone (icon + text)
- [ ] All images have alt text; decorative images `alt=""`
- [ ] 3D/2D viewer has an equivalent text findings list
- [ ] SVG regions have `<title>` in current language
- [ ] Content reflows at 320 px without horizontal scroll (except viewer canvas)
- [ ] Text resizable to 200% without loss

## Operable
- [ ] Everything reachable by keyboard; visible focus indicator (≥ 2 px, contrast ≥ 3:1)
- [ ] Viewer keyboard: arrows rotate, +/− zoom, R reset, Tab through findings list
- [ ] Focus not obscured by sticky headers/sheets (2.4.11)
- [ ] Target size ≥ 24×24 px (2.5.8); primary actions 44×44 px
- [ ] No time limits except security session (with warning and extend option)
- [ ] Dragging alternatives exist (2.5.7) — buttons for rotate/zoom
- [ ] `prefers-reduced-motion` respected

## Understandable
- [ ] `lang` attribute set per locale
- [ ] Labels and instructions for every input; errors identified in text and linked to field
- [ ] Consistent navigation and component behaviour
- [ ] Redundant entry avoided (3.3.7); accessible authentication without cognitive test (3.3.8) — allow password managers, passkeys

## Robust
- [ ] Valid semantic HTML; ARIA only when needed
- [ ] Status messages via `aria-live` (processing progress, saved, errors)
- [ ] Tested with axe (0 serious/critical) and one screen reader (NVDA or VoiceOver)
