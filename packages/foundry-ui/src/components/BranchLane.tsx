import * as React from "react";
import { cn } from "../lib/cn";

/** Tiny ahead/behind indicator shown inline in lists. */
export const AheadBehind: React.FC<{
  ahead: number;
  behind: number;
  className?: string;
}> = ({ ahead, behind, className }) => (
  <span className={cn("inline-flex items-center gap-1 text-xs text-fg-secondary tabular-nums", className)}>
    <span className="inline-flex items-center gap-0.5 text-state-success">
      <span>↑</span>
      <span>{ahead}</span>
    </span>
    <span className="text-fg-tertiary">/</span>
    <span className="inline-flex items-center gap-0.5 text-state-warn">
      <span>↓</span>
      <span>{behind}</span>
    </span>
  </span>
);
