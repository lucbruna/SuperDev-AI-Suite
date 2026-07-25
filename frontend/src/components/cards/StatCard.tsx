"use client";

import { type ReactNode } from "react";
import { cn } from "@/utils/cn";

type TrendDirection = "up" | "down" | "neutral";

interface StatCardProps {
  icon: ReactNode;
  value: string | number;
  label: string;
  trend?: {
    value: string;
    direction: TrendDirection;
  };
  className?: string;
}

const trendStyles: Record<TrendDirection, string> = {
  up: "text-green-600 bg-green-50 dark:text-green-400 dark:bg-green-950",
  down: "text-red-600 bg-red-50 dark:text-red-400 dark:bg-red-950",
  neutral: "text-surface-600 bg-surface-50 dark:text-surface-400 dark:bg-surface-800",
};

const trendIcons: Record<TrendDirection, string> = {
  up: "↑",
  down: "↓",
  neutral: "→",
};

export function StatCard({ icon, value, label, trend, className }: StatCardProps) {
  return (
    <div
      className={cn(
        "rounded-xl border border-surface-200 bg-white p-5 shadow-sm dark:border-surface-700 dark:bg-surface-900",
        className,
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-50 text-primary-600 dark:bg-primary-950 dark:text-primary-400">
          {icon}
        </div>
      </div>
      <div className="mt-4">
        <p className="text-2xl font-bold text-surface-900 dark:text-surface-50">
          {value}
        </p>
        <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">
          {label}
        </p>
      </div>
      {trend && (
        <div
          className={cn(
            "mt-4 inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium",
            trendStyles[trend.direction],
          )}
        >
          <span>{trendIcons[trend.direction]}</span>
          <span>{trend.value}</span>
        </div>
      )}
    </div>
  );
}
