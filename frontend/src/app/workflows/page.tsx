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
      <WorkflowCanvas />
    </DashboardLayout>
  );
}
