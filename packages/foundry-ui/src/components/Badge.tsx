import * as React from "react";
import { cn } from "../lib/cn";

export const Badge: React.FC<React.HTMLAttributes<HTMLSpanElement>> = ({
  className,
  children,
  ...props
}) => (
  <span
    className={cn(
      "inline-flex items-center gap-1 rounded-pill bg-white/5 border border-white/10 px-2 py-0.5 text-[11px] text-fg-secondary",
      className,
    )}
    {...props}
  >
    {children}
  </span>
);
