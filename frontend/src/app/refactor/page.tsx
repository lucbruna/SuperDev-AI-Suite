"use client";

import { RefactorPanel } from "../../components/refactor/RefactorPanel";

export default function RefactorPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-bold text-surface-900 dark:text-surface-50">Multi-File Refactoring</h1>
        <p className="text-sm text-surface-500">Search & replace, rename symbols, and extract functions across your codebase</p>
      </div>
      <RefactorPanel />
    </div>
  );
}