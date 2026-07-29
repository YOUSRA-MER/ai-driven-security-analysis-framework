import type { ButtonHTMLAttributes } from "react";
import { Spinner } from "./Spinner";
import { cx } from "./utils";

export type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";
export type ButtonSize = "xs" | "sm" | "md" | "lg";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  iconOnly?: boolean;
  loading?: boolean;
  loadingLabel?: string;
  size?: ButtonSize;
  variant?: ButtonVariant;
}

export function Button({
  children,
  className,
  disabled,
  iconOnly = false,
  loading = false,
  loadingLabel = "Loading",
  size = "md",
  type = "button",
  variant = "secondary",
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      className={cx(
        "ui-button",
        `ui-button--${variant}`,
        `ui-button--${size}`,
        iconOnly && "ui-button--icon",
        loading && "is-loading",
        className,
      )}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      {...props}
    >
      <span className="ui-button__content">{children}</span>
      {loading && (
        <span className="ui-button__loader">
          <Spinner size={size === "xs" ? "xs" : "sm"} />
          <span className="ui-visually-hidden">{loadingLabel}</span>
        </span>
      )}
    </button>
  );
}
