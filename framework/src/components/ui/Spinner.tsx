import type { HTMLAttributes } from "react";
import { cx } from "./utils";

export type SpinnerSize = "xs" | "sm" | "md" | "lg";

export interface SpinnerProps extends HTMLAttributes<HTMLSpanElement> {
  label?: string;
  size?: SpinnerSize;
}

export function Spinner({ className, label, size = "md", ...props }: SpinnerProps) {
  return (
    <span
      className={cx("ui-spinner", `ui-spinner--${size}`, className)}
      role={label ? "status" : undefined}
      aria-label={label}
      aria-hidden={label ? undefined : true}
      {...props}
    />
  );
}
