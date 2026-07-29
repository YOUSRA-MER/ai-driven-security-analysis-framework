import { cloneElement, useId, type ReactElement } from "react";
import { cx } from "./utils";

type TooltipPlacement = "top" | "right" | "bottom" | "left";
type TooltipChildProps = { "aria-describedby"?: string };

export interface TooltipProps {
  children: ReactElement<TooltipChildProps>;
  className?: string;
  content: string;
  placement?: TooltipPlacement;
}

export function Tooltip({ children, className, content, placement = "top" }: TooltipProps) {
  const id = useId();
  const describedBy = [children.props["aria-describedby"], id].filter(Boolean).join(" ");

  return (
    <span className={cx("ui-tooltip", className)}>
      {cloneElement(children, { "aria-describedby": describedBy })}
      <span
        id={id}
        role="tooltip"
        className={cx("ui-tooltip__content", `ui-tooltip__content--${placement}`)}
      >
        {content}
      </span>
    </span>
  );
}
