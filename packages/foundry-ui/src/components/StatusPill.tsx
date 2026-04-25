import * as React from "react";
import { cn } from "../lib/cn";
import type { BranchState, ReadinessState } from "../types";

type Pill = {
  label: string;
  className: string;
};

const BRANCH_STATE_PILL: Record<BranchState, Pill> = {
  active: { label: "Active", className: "bg-state-success/15 text-state-success border-state-success/30" },
  merged: { label: "Merged", className: "bg-accent-violet/15 text-accent-violet border-accent-violet/30" },
  stale: { label: "Stale", className: "bg-state-warn/15 text-state-warn border-state-warn/30" },
  orphaned: { label: "Orphaned", className: "bg-state-danger/15 text-state-danger border-state-danger/30" },
  archived: { label: "Archived", className: "bg-white/5 text-fg-tertiary border-white/10" },
};

const READINESS_PILL: Record<ReadinessState, Pill> = {
  ready: { label: "Ready to merge", className: "bg-state-success/15 text-state-success border-state-success/30" },
  needs_rebase: { label: "Needs rebase", className: "bg-state-warn/15 text-state-warn border-state-warn/30" },
  needs_review: { label: "Needs review", className: "bg-accent-blue/15 text-accent-blue border-accent-blue/30" },
  at_risk: { label: "At risk", className: "bg-state-danger/15 text-state-danger border-state-danger/30" },
  failing_checks: { label: "Failing checks", className: "bg-state-danger/15 text-state-danger border-state-danger/30" },
  draft: { label: "Draft", className: "bg-white/5 text-fg-tertiary border-white/10" },
};

export interface BranchStatePillProps {
  state: BranchState;
  className?: string;
}

export const BranchStatePill: React.FC<BranchStatePillProps> = ({ state, className }) => {
  const pill = BRANCH_STATE_PILL[state];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-pill border px-2 py-0.5 text-[11px] font-medium uppercase tracking-wide",
        pill.className,
        className,
      )}
    >
      {pill.label}
    </span>
  );
};

export interface ReadinessPillProps {
  readiness: ReadinessState;
  className?: string;
}

export const ReadinessPill: React.FC<ReadinessPillProps> = ({ readiness, className }) => {
  const pill = READINESS_PILL[readiness];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-pill border px-2 py-0.5 text-[11px] font-medium",
        pill.className,
        className,
      )}
    >
      {pill.label}
    </span>
  );
};
