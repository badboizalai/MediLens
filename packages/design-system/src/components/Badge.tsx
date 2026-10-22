import type { CSSProperties } from "react";
import { type SeverityKey, tokens } from "../tokens/tokens";

/** BR-020: severity is never colour-only; every level pairs a glyph and a text label. */
const GLYPH: Record<SeverityKey, string> = {
  monitor: "◉",
  mild: "◔",
  moderate: "◑",
  severe: "●",
  spread: "✳",
  reference: "ⓘ",
};

export interface SeverityBadgeProps {
  severity: SeverityKey;
  locale?: "vi" | "en";
}

export function SeverityBadge({ severity, locale = "vi" }: SeverityBadgeProps) {
  const t = tokens.color.severity[severity];
  const label = locale === "vi" ? t.labelVi : t.labelEn;
  const style = { "--ml-badge-color": `var(--ml-color-severity-${severity})` } as CSSProperties;
  return (
    <span className={`ml-badge ml-badge--${severity}`} style={style}>
      <span className="ml-badge__glyph" aria-hidden="true">{GLYPH[severity]}</span>
      {label}
    </span>
  );
}
