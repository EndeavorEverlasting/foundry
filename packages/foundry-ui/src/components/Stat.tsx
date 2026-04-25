import * as React from "react";
import { cn } from "../lib/cn";

export interface StatProps extends React.HTMLAttributes<HTMLDivElement> {
  label: string;
  value: React.ReactNode;
  hint?: React.ReactNode;
  tone?: "neutral" | "success" | "warn" | "danger";
}

const toneClasses: Record<NonNullable<StatProps["tone"]>, string> = {
  neutral: "text-fg-primary",
  success: "text-state-success",
  warn: "text-state-warn",
  danger: "text-state-danger",
};

export const Stat: React.FC<StatProps> = ({
  label,
  value,
  hint,
  tone = "neutral",
  className,
  ...props
}) => (
  <div
    className={cn(
      "flex flex-col gap-1 px-4 py-3 rounded-lg border border-white/5 bg-surface/50",
      className,
    )}
    {...props}
  >
    <span className="text-[11px] uppercase tracking-wide text-fg-tertiary font-medium">
      {label}
    </span>
    <span className={cn("text-2xl font-semibold tabular-nums tracking-tight", toneClasses[tone])}>
      {value}
    </span>
    {hint ? <span className="text-xs text-fg-tertiary">{hint}</span> : null}
  </div>
);
