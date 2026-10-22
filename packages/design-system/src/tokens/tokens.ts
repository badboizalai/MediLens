import tokens from "../../tokens.json";

export { tokens };
export type SeverityKey = keyof typeof tokens.color.severity;
export const severityKeys = Object.keys(tokens.color.severity) as SeverityKey[];

export const kebab = (s: string) => s.replace(/[A-Z]/g, (c) => `-${c.toLowerCase()}`);
type Mode = "light" | "dark";

function themed(mode: Mode): string[] {
  const out: string[] = [];
  for (const [group, entries] of Object.entries(tokens.color)) {
    for (const [name, v] of Object.entries(entries as Record<string, Record<string, string>>)) {
      out.push(`--ml-color-${kebab(group)}-${kebab(name)}: ${v[mode]};`);
    }
  }
  return out;
}

function flat(prefix: string, obj: Record<string, string | number>): string[] {
  return Object.entries(obj).map(([k, v]) => `--ml-${prefix}-${k}: ${v};`);
}

/** CSS custom properties. Light is the default; dark via [data-theme="dark"]. */
export function cssVariables(): string {
  const shared = [
    ...flat("font-family", tokens.font.family),
    ...flat("font-size", tokens.font.size),
    ...flat("line-height", tokens.font.lineHeight),
    ...flat("font-weight", tokens.font.weight),
    ...flat("space", tokens.space),
    ...flat("radius", tokens.radius),
    ...flat("motion", tokens.motion),
    ...flat("a11y", tokens.a11y),
  ];
  const block = (sel: string, lines: string[]) => `${sel} {\n  ${lines.join("\n  ")}\n}`;
  return [
    block(":root", [...themed("light"), ...shared]),
    block('[data-theme="dark"]', themed("dark")),
    "@media (prefers-reduced-motion: reduce) {\n  :root {\n    --ml-motion-fast: 0ms;\n    --ml-motion-normal: 0ms;\n    --ml-motion-slow: 0ms;\n  }\n}",
  ].join("\n");
}
