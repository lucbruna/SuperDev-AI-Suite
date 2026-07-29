"use client";

import dynamic from "next/dynamic";
import { DashboardLayout } from "@/components/DashboardLayout";

const WorkflowCanvas = dynamic(
  () => import("@/workflow/WorkflowCanvas").then((m) => ({ default: m.WorkflowCanvas })),
  { ssr: false, loading: () => <p className="text-surface-400">Carregando canvas...</p> }
);

export default function WorkflowsPage() {
  return (
    <DashboardLayout>
      <h1 className="mb-6 text-2xl font-bold text-surface-900 dark:text-surface-50">Workflows</h1>
      <WorkflowCanvas />
    </DashboardLayout>
  );
}
