"use client";

import { useState } from "react";

interface ReviewComment {
  id: string;
  author: string;
  file: string;
  line: number;
  body: string;
  resolved: boolean;
  timestamp: string;
}

export function ReviewPanel() {
  const [comments] = useState<ReviewComment[]>([
    { id: "c1", author: "AI Reviewer", file: "src/main.py", line: 42, body: "Consider adding input validation here", resolved: false, timestamp: "2m ago" },
    { id: "c2", author: "AI Reviewer", file: "src/agent.py", line: 18, body: "This function could be async for better performance", resolved: true, timestamp: "5m ago" },
    { id: "c3", author: "AI Reviewer", file: "src/utils.py", line: 7, body: "Unused import 'os' detected", resolved: false, timestamp: "3m ago" },
  ]);
  const [filter, setFilter] = useState<"all" | "open" | "resolved">("all");

  const filtered = comments.filter((c) => filter === "all" || (filter === "open" && !c.resolved) || (filter === "resolved" && c.resolved));

  return (
    <div className="rounded-xl border dark:border-surface-700">
      <div className="flex items-center justify-between border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
        <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">Code Review ({comments.filter((c) => !c.resolved).length} open)</span>
        <div className="flex gap-1">
          {(["all", "open", "resolved"] as const).map((f) => (
            <button key={f} onClick={() => setFilter(f)} className={`rounded px-2 py-0.5 text-[9px] ${filter === f ? "bg-primary-600 text-white" : "bg-surface-200 text-surface-600 dark:bg-surface-700 dark:text-surface-300"}`}>
              {f}
            </button>
          ))}
        </div>
      </div>
      <div className="divide-y dark:divide-surface-700">
        {filtered.map((c) => (
          <div key={c.id} className={`p-3 ${c.resolved ? "opacity-50" : ""}`}>
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium text-surface-900 dark:text-surface-50">{c.author}</span>
                  <span className="text-[9px] font-mono text-surface-500">{c.file}:{c.line}</span>
                </div>
                <p className="mt-1 text-xs text-surface-600 dark:text-surface-400">{c.body}</p>
              </div>
              <span className={`rounded-full px-2 py-0.5 text-[9px] ${c.resolved ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
                {c.resolved ? "Resolved" : "Open"}
              </span>
            </div>
            <p className="mt-1 text-[9px] text-surface-400">{c.timestamp}</p>
          </div>
        ))}
      </div>
    </div>
  );
}