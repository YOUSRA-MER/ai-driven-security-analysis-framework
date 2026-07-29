import type { HTMLAttributes } from "react";
import { cx } from "./utils";

export interface DividerProps extends HTMLAttributes<HTMLHRElement> {
  orientation?: "horizontal" | "vertical";
  spaced?: boolean;
}

export function Divider({
  className,
  orientation = "horizontal",
  spaced = false,
  ...props
}: DividerProps) {
  return (
    <hr
      className={cx(
        "ui-divider",
        `ui-divider--${orientation}`,
        spaced && "ui-divider--spaced",
        className,
      )}
      aria-orientation={orientation}
      {...props}
    />
  );
}
