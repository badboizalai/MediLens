import { Slot } from "@radix-ui/react-slot";
import type { ButtonHTMLAttributes } from "react";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger";
  /** Render the child element (e.g. a link) with button styling. */
  asChild?: boolean;
}

export function Button({ variant = "primary", asChild, className, type = "button", ...props }: ButtonProps) {
  const Comp = asChild ? Slot : "button";
  return <Comp {...(asChild ? {} : { type })} className={`ml-btn ml-btn--${variant} ${className ?? ""}`.trim()} {...props} />;
}
