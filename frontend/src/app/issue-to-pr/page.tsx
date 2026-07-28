"use client";

import { IssueToPR } from "@/components/issue-to-pr/IssueToPR";
import { IssueToPRConfig } from "@/components/issue-to-pr/IssueToPRConfig";

export default function IssueToPRPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-bold text-surface-900 dark:text-surface-50">Issue → PR Automation</h1>
        <p className="text-sm text-surface-500">
          Automatically generate pull requests from GitHub issues — triggered by labels or slash commands
        </p>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <IssueToPR />
        <IssueToPRConfig />
      </div>
    </div>
  );
}