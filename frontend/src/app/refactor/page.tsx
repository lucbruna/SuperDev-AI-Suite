"use client";

import { DashboardLayout } from "@/components/DashboardLayout";
import { RefactorPanel } from "@/components/refactor/RefactorPanel";

export default function RefactorPage() {
  return (
    <DashboardLayout>
      <h1 className="mb-6 text-2xl font-bold text-surface-900 dark:text-surface-50">Refatoração</h1>
      <RefactorPanel />
    </DashboardLayout>
  );
}
