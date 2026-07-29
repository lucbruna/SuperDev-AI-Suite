"use client";

import { DashboardLayout } from "@/components/DashboardLayout";
import { AITerminal } from "@/components/terminal/ai/AITerminal";

export default function RuntimePage() {
  return (
    <DashboardLayout>
      <h1 className="mb-1 text-2xl font-bold text-surface-900 dark:text-surface-50">Runtime</h1>
      <p className="mb-6 text-sm text-surface-500">Terminal de execução de código</p>
      <AITerminal />
    </DashboardLayout>
  );
}
