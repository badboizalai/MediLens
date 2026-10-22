import type { HTMLAttributes, ReactNode } from "react";

export interface CardProps extends Omit<HTMLAttributes<HTMLElement>, "title"> {
  title?: ReactNode;
}

export function Card({ title, children, className, ...props }: CardProps) {
  return (
    <section className={`ml-card ${className ?? ""}`.trim()} {...props}>
      {title ? <h3 className="ml-card__title">{title}</h3> : null}
      {children}
    </section>
  );
}
