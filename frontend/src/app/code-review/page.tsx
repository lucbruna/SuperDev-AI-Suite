"use client";

import { CodeReviewPanel } from "@/components/code-review/CodeReviewPanel";

export default function CodeReviewPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-bold text-surface-900 dark:text-surface-50">AI Code Review</h1>
        <p className="text-sm text-surface-500">Automated code review with GitHub Checks integration — catches bugs, security issues, and style problems before merge</p>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <CodeReviewPanel />
        <div className="rounded-xl border dark:border-surface-700">
          <div className="border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
            <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">Rules Applied</span>
          </div>
          <div className="space-y-1 p-4">
            {["Print Statement", "Debug Breakpoint", "Naked Except", "Hardcoded URL", "Console.log", "TypeScript Any", "Bare Except"].map((r) => (
              <div key={r} className="flex items-center gap-2 rounded-lg bg-surface-50 px-3 py-2 text-xs dark:bg-surface-800 dark:text-surface-300">
                <span className="h-1.5 w-1.5 rounded-full bg-primary-500" />
                {r}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}