import type { Config } from "tailwindcss";
import { kebab, tokens } from "./tokens";

const v = (name: string) => `var(--ml-${name})`;

const colorGroup = (group: keyof typeof tokens.color) =>
  Object.fromEntries(Object.keys(tokens.color[group]).map((k) => [k, v(`color-${kebab(group)}-${kebab(k)}`)]));

const map = (prefix: string, o: object) => Object.fromEntries(Object.keys(o).map((k) => [k, v(`${prefix}-${k}`)]));

/** Tailwind preset: every value resolves to a CSS variable so light/dark switch without rebuilds. */
const preset: Partial<Config> = {
  darkMode: ["selector", '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        brand: colorGroup("brand"),
        severity: colorGroup("severity"),
        feedback: colorGroup("feedback"),
      },
      fontFamily: map("font-family", tokens.font.family),
      fontSize: map("font-size", tokens.font.size),
      spacing: map("space", tokens.space),
      borderRadius: map("radius", tokens.radius),
      minHeight: { target: v("a11y-minTarget"), "target-primary": v("a11y-primaryTarget") },
      minWidth: { target: v("a11y-minTarget"), "target-primary": v("a11y-primaryTarget") },
    },
  },
};

export default preset;
