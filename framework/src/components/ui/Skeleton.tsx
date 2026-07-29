import type { CSSProperties, HTMLAttributes } from "react";
import { cx } from "./utils";

export interface SkeletonProps extends HTMLAttributes<HTMLSpanElement> {
  circle?: boolean;
  height?: CSSProperties["height"];
  width?: CSSProperties["width"];
}

export function Skeleton({ circle = false, className, height, style, width = "100%", ...props }: SkeletonProps) {
  return (
    <span
      className={cx("ui-skeleton", circle && "ui-skeleton--circle", className)}
      style={{ width, height, ...style }}
      aria-hidden="true"
      {...props}
    />
  );
}
