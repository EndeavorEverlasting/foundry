import * as React from "react";
import { cn } from "../lib/cn";

export interface PageHeaderProps {
  eyebrow?: React.ReactNode;
  title: React.ReactNode;
  description?: React.ReactNode;
  actions?: React.ReactNode;
  className?: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  eyebrow,
  title,
  description,
  actions,
  className,
}) => (
  <header className={cn("flex flex-wrap items-end justify-between gap-4 pb-4 mb-6 border-b border-white/5", className)}>
    <div className="flex flex-col gap-1 min-w-0">
      {eyebrow ? (
        <span className="text-[11px] font-medium uppercase tracking-wider text-fg-tertiary">
          {eyebrow}
        </span>
      ) : null}
      <h1 className="text-xl md:text-2xl font-semibold text-fg-primary tracking-tight truncate">
        {title}
      </h1>
      {description ? (
        <p className="text-sm text-fg-tertiary max-w-prose">{description}</p>
      ) : null}
    </div>
    {actions ? <div className="flex items-center gap-2 shrink-0">{actions}</div> : null}
  </header>
);
