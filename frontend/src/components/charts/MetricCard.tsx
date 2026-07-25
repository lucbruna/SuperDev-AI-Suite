"use client";

import { type ReactNode, useMemo } from "react";
import { cn } from "@/utils/cn";

type TrendDirection = "up" | "down";

interface SparklineData {
  values: number[];
  color?: string;
}

interface MetricCardProps {
  icon?: ReactNode;
  label: string;
  value: string | number;
  trend?: {
    direction: TrendDirection;
    percentage: number;
  };
  sparkline?: SparklineData;
  className?: string;
}

export function MetricCard({
  icon,
  label,
  value,
  trend,
  sparkline,
  className,
}: MetricCardProps) {
  const sparklinePath = useMemo(() => {
    if (!sparkline || sparkline.values.length < 2) return "";
    const values = sparkline.values;
    const max = Math.max(...values);
    const min = Math.min(...values);
    const range = max - min || 1;
    const w = 80;
    const h = 28;
    const step = w / (values.length - 1);

    return values
      .map((v, i) => {
        const x = i * step;
        const y = h - ((v - min) / range) * h;
        return `${i === 0 ? "M" : "L"} ${x} ${y}`;
      })
      .join(" ");
  }, [sparkline]);

  return (
    <div
      className={cn(
        "rounded-xl border border-surface-200 bg-white p-5 shadow-sm dark:border-surface-700 dark:bg-surface-900",
        className,
      )}
    >
      <div className="flex items-start justify-between">
        {icon && (
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-surface-100 text-surface-600 dark:bg-surface-800 dark:text-surface-400">
            {icon}
          </div>
        )}
        {trend && (
          <div
            className={cn(
              "inline-flex items-center gap-0.5 rounded-full px-2 py-0.5 text-xs font-medium",
              trend.direction === "up"
                ? "bg-green-50 text-green-600 dark:bg-green-950 dark:text-green-400"
                : "bg-red-50 text-red-600 dark:bg-red-950 dark:text-red-400",
            )}
          >
            <span>{trend.direction === "up" ? "↑" : "↓"}</span>
            <span>{trend.percentage}%</span>
          </div>
        )}
      </div>

      <div className="mt-3">
        <p className="text-xs text-surface-500 dark:text-surface-400">{label}</p>
        <p className="mt-1 text-2xl font-bold text-surface-900 dark:text-surface-50">
          {value}
        </p>
      </div>

      {sparkline && sparkline.values.length >= 2 && (
        <div className="mt-3">
          <svg width="80" height="28" viewBox="0 0 80 28" className="overflow-visible">
            <path
              d={sparklinePath}
              fill="none"
              stroke={sparkline.color ?? "#3b82f6"}
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
      )}
    </div>
  );
}
