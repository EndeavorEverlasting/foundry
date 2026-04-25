import * as React from "react";
import { cn } from "../lib/cn";

export interface ConfidenceBadgeProps {
  value: number;
  className?: string;
}

function label(v: number): { text: string; tone: string } {
  if (v >= 0.8) return { text: "High confidence", tone: "text-state-success bg-state-success/15 border-state-success/30" };
  if (v >= 0.5) return { text: "Moderate confidence", tone: "text-state-warn bg-state-warn/15 border-state-warn/30" };
  if (v > 0) return { text: "Low confidence", tone: "text-fg-secondary bg-white/5 border-white/10" };
  return { text: "No evidence", tone: "text-fg-tertiary bg-white/5 border-white/10" };
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({ value, className }) => {
  const { text, tone } = label(value);
  const pct = Math.round(Math.max(0, Math.min(1, value)) * 100);
  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 rounded-pill border px-2.5 py-0.5 text-[11px] font-medium",
        tone,
        className,
      )}
      title={`Confidence: ${pct}% derived from evidence tier coverage.`}
    >
      <span className="tabular-nums">{pct}%</span>
      <span className="opacity-80">{text}</span>
    </span>
  );
};
