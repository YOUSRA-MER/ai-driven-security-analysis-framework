import type { HTMLAttributes } from "react";
import { cx } from "./utils";

export type BadgeTone = "neutral" | "brand" | "info" | "success" | "warning" | "danger" | "ai";

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  rounded?: boolean;
  size?: "sm" | "md";
  tone?: BadgeTone;
}

export function Badge({
  className,
  rounded = false,
  size = "md",
  tone = "neutral",
  ...props
}: BadgeProps) {
  return (
    <span
      className={cx(
        "ui-badge",
        `ui-badge--${tone}`,
        `ui-badge--${size}`,
        rounded && "ui-badge--rounded",
        className,
      )}
      {...props}
    />
  );
}
