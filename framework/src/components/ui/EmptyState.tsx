import type { HTMLAttributes, ReactNode } from "react";
import { cx } from "./utils";

export interface EmptyStateProps extends Omit<HTMLAttributes<HTMLDivElement>, "title"> {
  actions?: ReactNode;
  compact?: boolean;
  description?: ReactNode;
  icon?: ReactNode;
  title: ReactNode;
}

export function EmptyState({
  actions,
  className,
  compact = false,
  description,
  icon,
  title,
  ...props
}: EmptyStateProps) {
  return (
    <div className={cx("ui-empty-state", compact && "ui-empty-state--compact", className)} {...props}>
      {icon && <div className="ui-empty-state__icon" aria-hidden="true">{icon}</div>}
      <strong className="ui-empty-state__title">{title}</strong>
      {description && <p className="ui-empty-state__description">{description}</p>}
      {actions && <div className="ui-empty-state__actions">{actions}</div>}
    </div>
  );
}
