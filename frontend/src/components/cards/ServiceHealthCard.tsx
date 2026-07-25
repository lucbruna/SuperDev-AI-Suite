"use client";

import { cn } from "@/utils/cn";

type HealthStatus = "healthy" | "degraded" | "down";

interface ServiceHealthCardProps {
  serviceName: string;
  status: HealthStatus;
  uptimePercentage: number;
  latencyMs: number;
  lastChecked: string;
  className?: string;
}

const statusConfig: Record<HealthStatus, { dotColor: string; label: string; bgColor: string }> = {
  healthy: {
    dotColor: "bg-green-500",
    label: "Healthy",
    bgColor: "bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-400",
  },
  degraded: {
    dotColor: "bg-amber-500",
    label: "Degraded",
    bgColor: "bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-400",
  },
  down: {
    dotColor: "bg-red-500",
    label: "Down",
    bgColor: "bg-red-50 text-red-700 dark:bg-red-950 dark:text-red-400",
  },
};

function getTimeAgo(dateString: string): string {
  const diffMs = Date.now() - new Date(dateString).getTime();
  const diffSec = Math.floor(diffMs / 1000);
  if (diffSec < 60) return "just now";
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  return `${Math.floor(diffHr / 24)}d ago`;
}

export function ServiceHealthCard({
  serviceName,
  status,
  uptimePercentage,
  latencyMs,
  lastChecked,
  className,
}: ServiceHealthCardProps) {
  const config = statusConfig[status];

  return (
    <div
      className={cn(
        "rounded-xl border border-surface-200 bg-white p-5 shadow-sm dark:border-surface-700 dark:bg-surface-900",
        className,
      )}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className={cn("h-3 w-3 rounded-full", config.dotColor)} />
          <h3 className="text-sm font-semibold text-surface-900 dark:text-surface-50">
            {serviceName}
          </h3>
        </div>
        <span
          className={cn(
            "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
            config.bgColor,
          )}
        >
          {config.label}
        </span>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-4">
        <div>
          <p className="text-xs text-surface-500 dark:text-surface-400">Uptime</p>
          <p className="mt-0.5 text-sm font-semibold text-surface-900 dark:text-surface-50">
            {uptimePercentage}%
          </p>
        </div>
        <div>
          <p className="text-xs text-surface-500 dark:text-surface-400">Latency</p>
          <p className="mt-0.5 text-sm font-semibold text-surface-900 dark:text-surface-50">
            {latencyMs}ms
          </p>
        </div>
        <div>
          <p className="text-xs text-surface-500 dark:text-surface-400">Checked</p>
          <p className="mt-0.5 text-sm font-semibold text-surface-900 dark:text-surface-50">
            {getTimeAgo(lastChecked)}
          </p>
        </div>
      </div>
    </div>
  );
}
