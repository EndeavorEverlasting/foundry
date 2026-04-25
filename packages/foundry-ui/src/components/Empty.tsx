import * as React from "react";
import { cn } from "../lib/cn";

export interface EmptyProps {
  title: string;
  description?: React.ReactNode;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}

export const Empty: React.FC<EmptyProps> = ({
  title,
  description,
  icon,
  action,
  className,
}) => (
  <div
    className={cn(
      "flex flex-col items-center justify-center text-center gap-3 py-12 px-6 rounded-lg border border-dashed border-white/8 bg-surface/30",
      className,
    )}
  >
    {icon ? <div className="text-fg-tertiary">{icon}</div> : null}
    <h3 className="text-sm font-medium text-fg-primary">{title}</h3>
    {description ? (
      <p className="text-sm text-fg-tertiary max-w-prose leading-relaxed">{description}</p>
    ) : null}
    {action ? <div className="mt-2">{action}</div> : null}
  </div>
);
