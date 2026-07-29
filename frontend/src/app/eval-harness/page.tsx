"use client";

import { DashboardLayout } from "@/components/DashboardLayout";
import { EvalHarnessPanel } from "@/components/eval-harness/EvalHarnessPanel";

export default function EvalHarnessPage() {
  return (
    <DashboardLayout>
      <h1 className="mb-6 text-2xl font-bold text-surface-900 dark:text-surface-50">Eval Harness</h1>
      <EvalHarnessPanel />
    </DashboardLayout>
  );
}
