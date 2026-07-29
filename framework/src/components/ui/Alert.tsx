import type { HTMLAttributes, ReactNode } from "react";
import { AlertCircle, AlertTriangle, CheckCircle2, Info, X } from "lucide-react";
import { Button } from "./Button";
import { cx } from "./utils";

export type AlertVariant = "neutral" | "info" | "success" | "warning" | "danger" | "error";

export interface AlertProps extends HTMLAttributes<HTMLDivElement> {
  icon?: ReactNode;
  onDismiss?: () => void;
  title?: string;
  variant?: AlertVariant;
}

const icons = {
  neutral: Info,
  info: Info,
  success: CheckCircle2,
  warning: AlertTriangle,
  danger: AlertCircle,
  error: AlertCircle,
};

export function Alert({
  children,
  className,
  icon,
  onDismiss,
  role,
  title,
  variant = "neutral",
  ...props
}: AlertProps) {
  const Icon = icons[variant];
  return (
    <div
      className={cx("ui-alert", `ui-alert--${variant}`, className)}
      role={role ?? (["danger", "error"].includes(variant) ? "alert" : "status")}
      aria-atomic="true"
      {...props}
    >
      <span className="ui-alert__icon" aria-hidden="true">{icon ?? <Icon />}</span>
      <div className="ui-alert__content">
        {title && <strong className="ui-alert__title">{title}</strong>}
        {children}
      </div>
      {onDismiss && (
        <Button
          variant="ghost"
          size="xs"
          iconOnly
          aria-label={`Dismiss ${variant === "danger" ? "error" : variant} notification`}
          onClick={onDismiss}
        >
          <X />
        </Button>
      )}
    </div>
  );
}
