"use client";

import { DashboardLayout } from "@/components/DashboardLayout";
import { EvalPanel } from "@/components/evals/EvalPanel";

export default function EvalsPage() {
  return (
    <DashboardLayout>
      <h1 className="mb-6 text-2xl font-bold text-surface-900 dark:text-surface-50">Avaliações</h1>
      <EvalPanel />
    </DashboardLayout>
  );
}
