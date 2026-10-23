import type { HTMLAttributes, ReactNode } from "react";

const GLYPH = { info: "ⓘ", success: "✓", warning: "▲", danger: "✕" } as const;

export interface AlertProps extends Omit<HTMLAttributes<HTMLDivElement>, "title"> {
  tone?: keyof typeof GLYPH;
  title?: ReactNode;
}

/** danger/warning interrupt (role=alert); info/success are polite (role=status). */
export function Alert({ tone = "info", title, children, className, ...props }: AlertProps) {
  const role = tone === "danger" || tone === "warning" ? "alert" : "status";
  return (
    <div role={role} className={`ml-alert ml-alert--${tone} ${className ?? ""}`.trim()} {...props}>
      <span className="ml-alert__glyph" aria-hidden="true">{GLYPH[tone]}</span>
      <div>
        {title ? <div className="ml-alert__title">{title}</div> : null}
        {children}
      </div>
    </div>
  );
}
