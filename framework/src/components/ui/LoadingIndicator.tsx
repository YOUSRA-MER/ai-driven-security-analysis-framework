import type { HTMLAttributes } from "react";
import { Spinner } from "./Spinner";
import { cx } from "./utils";

export interface LoadingIndicatorProps extends HTMLAttributes<HTMLDivElement> {
  inline?: boolean;
  label: string;
}

export function LoadingIndicator({ className, inline = false, label, ...props }: LoadingIndicatorProps) {
  return (
    <div
      className={cx("ui-loading-indicator", inline && "ui-loading-indicator--inline", className)}
      role="status"
      aria-live="polite"
      {...props}
    >
      <Spinner size="sm" />
      <span>{label}</span>
    </div>
  );
}
