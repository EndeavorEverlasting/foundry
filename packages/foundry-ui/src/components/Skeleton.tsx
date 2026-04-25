import * as React from "react";
import { cn } from "../lib/cn";

export const Skeleton: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  ...props
}) => (
  <div
    className={cn(
      "animate-pulse rounded-md bg-white/5",
      className,
    )}
    {...props}
  />
);

export const SkeletonText: React.FC<{ lines?: number; className?: string }> = ({
  lines = 3,
  className,
}) => (
  <div className={cn("flex flex-col gap-2", className)}>
    {Array.from({ length: lines }).map((_, i) => (
      <Skeleton
        key={i}
        className={cn("h-3", i === lines - 1 ? "w-2/3" : "w-full")}
      />
    ))}
  </div>
);
