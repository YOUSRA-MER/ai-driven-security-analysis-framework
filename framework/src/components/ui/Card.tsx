import type { HTMLAttributes } from "react";
import { cx } from "./utils";

type CardElement = "article" | "div" | "section";
type CardPadding = "none" | "sm" | "md" | "lg";
type CardVariant = "default" | "raised" | "inset";

export interface CardProps extends HTMLAttributes<HTMLElement> {
  as?: CardElement;
  padding?: CardPadding;
  variant?: CardVariant;
}

export function Card({
  as: Component = "div",
  className,
  padding = "md",
  variant = "default",
  ...props
}: CardProps) {
  return (
    <Component
      className={cx(
        "ui-card",
        variant !== "default" && `ui-card--${variant}`,
        padding !== "none" && `ui-card--padding-${padding}`,
        className,
      )}
      {...props}
    />
  );
}
