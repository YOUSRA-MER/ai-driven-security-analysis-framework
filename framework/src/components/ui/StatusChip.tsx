import type { HTMLAttributes } from "react";
import type { BadgeTone } from "./Badge";
import { Spinner } from "./Spinner";
import { cx } from "./utils";

export interface StatusChipProps extends HTMLAttributes<HTMLSpanElement> {
  dot?: boolean;
  loading?: boolean;
  rounded?: boolean;
  size?: "sm" | "md";
  tone?: BadgeTone;
}

export function StatusChip({
  children,
  className,
  dot = false,
  loading = false,
  rounded = false,
  size = "md",
  tone = "neutral",
  ...props
}: StatusChipProps) {
  return (
    <span
      className={cx(
        "ui-status-chip",
        `ui-status-chip--${tone}`,
        `ui-status-chip--${size}`,
        rounded && "ui-status-chip--rounded",
        className,
      )}
      {...props}
    >
      {loading ? <Spinner size="xs" /> : dot ? <span className="ui-status-chip__dot" aria-hidden="true" /> : null}
      <span>{children}</span>
    </span>
  );
}
