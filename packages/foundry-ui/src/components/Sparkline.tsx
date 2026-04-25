import * as React from "react";
import { cn } from "../lib/cn";

export interface SparklineProps {
  values: number[];
  width?: number;
  height?: number;
  className?: string;
  stroke?: string;
}

export const Sparkline: React.FC<SparklineProps> = ({
  values,
  width = 120,
  height = 28,
  className,
  stroke = "currentColor",
}) => {
  if (values.length === 0) {
    return <svg className={cn(className)} width={width} height={height} />;
  }
  const max = Math.max(...values);
  const min = Math.min(...values);
  const range = Math.max(1, max - min);
  const step = width / Math.max(1, values.length - 1);
  const points = values
    .map((v, i) => {
      const x = i * step;
      const y = height - ((v - min) / range) * height;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  return (
    <svg
      className={cn(className)}
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      aria-hidden
    >
      <polyline
        fill="none"
        stroke={stroke}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        points={points}
      />
    </svg>
  );
};
