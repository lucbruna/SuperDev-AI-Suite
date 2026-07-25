"use client";

import { useState, useMemo } from "react";
import { cn } from "@/utils/cn";

type LogLevel = "debug" | "info" | "warn" | "error" | "fatal";

interface LogEntry {
  id: string;
  timestamp: string;
  level: LogLevel;
  source: string;
  message: string;
  context?: Record<string, unknown>;
}

interface LogsTableProps {
  logs?: LogEntry[];
  className?: string;
}

const levelConfig: Record<LogLevel, { label: string; color: string }> = {
  debug: { label: "DEBUG", color: "bg-surface-100 text-surface-600 dark:bg-surface-800 dark:text-surface-400" },
  info: { label: "INFO", color: "bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-400" },
  warn: { label: "WARN", color: "bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-400" },
  error: { label: "ERROR", color: "bg-red-50 text-red-700 dark:bg-red-950 dark:text-red-400" },
  fatal: { label: "FATAL", color: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300" },
};

const mockLogs: LogEntry[] = [
  { id: "l1", timestamp: "2026-07-24T14:32:10.123Z", level: "info", source: "api-server", message: "Request received: GET /api/v1/workflows", context: { method: "GET", path: "/api/v1/workflows", status: 200, duration: "45ms" } },
  { id: "l2", timestamp: "2026-07-24T14:32:09.456Z", level: "warn", source: "auth-service", message: "Token refresh rate limit approaching", context: { userId: "u_abc123", remaining: 10, resetAt: "2026-07-24T15:00:00Z" } },
  { id: "l3", timestamp: "2026-07-24T14:32:08.789Z", level: "error", source: "database", message: "Connection pool exhausted, retrying...", context: { poolSize: 10, active: 10, idle: 0, waitQueue: 3 } },
  { id: "l4", timestamp: "2026-07-24T14:32:07.012Z", level: "info", source: "worker", message: "Job completed: workflow-deploy-42", context: { jobId: "wf_deploy_42", duration: "2.3s", steps: 8, success: true } },
  { id: "l5", timestamp: "2026-07-24T14:32:06.345Z", level: "debug", source: "plugin-loader", message: "Loading plugin: gpt4-provider v2.1.0", context: { plugin: "gpt4-provider", version: "2.1.0", path: "/plugins/gpt4" } },
  { id: "l6", timestamp: "2026-07-24T14:32:05.678Z", level: "fatal", source: "monitoring", message: "Out of memory: process terminated", context: { pid: 1234, memoryUsage: "2.4GB", limit: "2GB" } },
  { id: "l7", timestamp: "2026-07-24T14:32:04.901Z", level: "info", source: "api-server", message: "Response sent: POST /api/v1/workflows/execute", context: { method: "POST", path: "/api/v1/workflows/execute", status: 201, duration: "1.2s" } },
  { id: "l8", timestamp: "2026-07-24T14:32:03.234Z", level: "warn", source: "file-watcher", message: "File change detected: src/app/page.tsx", context: { file: "src/app/page.tsx", event: "modify", watchId: "w_789" } },
];

export function LogsTable({ logs = mockLogs, className }: LogsTableProps) {
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const sortedLogs = useMemo(() => {
    return [...logs].sort((a, b) => {
      const diff = new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
      return sortOrder === "asc" ? diff : -diff;
    });
  }, [logs, sortOrder]);

  const toggleExpand = (id: string) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  const formatTime = (ts: string) => {
    const d = new Date(ts);
    return d.toLocaleTimeString("en-US", { hour12: false }) + "." + d.getMilliseconds().toString().padStart(3, "0");
  };

  if (logs.length === 0) {
    return (
      <div className={cn("flex items-center justify-center py-12 text-sm text-surface-400", className)}>
        No log entries available
      </div>
    );
  }

  return (
    <div className={cn("overflow-hidden rounded-xl border border-surface-200 dark:border-surface-700", className)}>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-surface-200 dark:divide-surface-700">
          <thead className="bg-surface-50 dark:bg-surface-800">
            <tr>
              <th className="w-8 px-2 py-3" />
              {[
                { key: "timestamp", label: "Timestamp" },
                { key: "level", label: "Level" },
                { key: "source", label: "Source" },
                { key: "message", label: "Message" },
              ].map((col) => (
                <th
                  key={col.key}
                  className={cn(
                    "px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-surface-500 dark:text-surface-400",
                    col.key === "timestamp" && "cursor-pointer select-none hover:text-surface-700 dark:hover:text-surface-200",
                  )}
                  onClick={() => col.key === "timestamp" && setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
                >
                  <div className="flex items-center gap-1">
                    {col.label}
                    {col.key === "timestamp" && (
                      <span className="text-[10px]">{sortOrder === "asc" ? "↑" : "↓"}</span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-200 bg-white font-mono text-xs dark:divide-surface-700 dark:bg-surface-900">
            {sortedLogs.map((log) => {
              const levelCfg = levelConfig[log.level];
              const isExpanded = expandedId === log.id;
              return (
                <tr key={log.id} className="group">
                  <td className="px-2 py-2">
                    <button
                      onClick={() => toggleExpand(log.id)}
                      className="rounded p-0.5 text-surface-400 hover:bg-surface-100 hover:text-surface-600 dark:hover:bg-surface-800 dark:hover:text-surface-300"
                    >
                      <svg
                        className={cn("h-3 w-3 transition-transform", isExpanded && "rotate-90")}
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </button>
                  </td>
                  <td className="whitespace-nowrap px-4 py-2 text-surface-500 dark:text-surface-400">
                    {formatTime(log.timestamp)}
                  </td>
                  <td className="whitespace-nowrap px-4 py-2">
                    <span className={cn("inline-flex items-center rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase", levelCfg.color)}>
                      {levelCfg.label}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-4 py-2 text-surface-600 dark:text-surface-400">
                    {log.source}
                  </td>
                  <td className="max-w-md truncate px-4 py-2 text-surface-900 dark:text-surface-50">
                    {log.message}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {expandedId && (
        <div className="border-t border-surface-200 bg-surface-50 p-4 dark:border-surface-700 dark:bg-surface-800">
          {(() => {
            const log = sortedLogs.find((l) => l.id === expandedId);
            if (!log) return null;
            return (
              <div className="space-y-3">
                <div>
                  <p className="text-[11px] font-semibold uppercase text-surface-500 dark:text-surface-400">
                    Full Message
                  </p>
                  <p className="mt-1 text-sm text-surface-900 dark:text-surface-50">
                    {log.message}
                  </p>
                </div>
                {log.context && Object.keys(log.context).length > 0 && (
                  <div>
                    <p className="text-[11px] font-semibold uppercase text-surface-500 dark:text-surface-400">
                      Context
                    </p>
                    <pre className="mt-1 overflow-x-auto rounded-lg bg-surface-100 p-3 font-mono text-xs text-surface-800 dark:bg-surface-900 dark:text-surface-200">
                      {JSON.stringify(log.context, null, 2)}
                    </pre>
                  </div>
                )}
                <div className="flex items-center gap-4 text-[11px] text-surface-400">
                  <span>ID: {log.id}</span>
                  <span>Timestamp: {new Date(log.timestamp).toISOString()}</span>
                </div>
              </div>
            );
          })()}
        </div>
      )}
    </div>
  );
}
