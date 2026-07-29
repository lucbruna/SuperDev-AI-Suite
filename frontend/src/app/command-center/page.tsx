"use client";

import { DashboardLayout } from "@/components/DashboardLayout";
import { KanbanBoard } from "@/components/command-center/KanbanBoard";

export default function CommandCenterPage() {
  return (
    <DashboardLayout>
      <h1 className="mb-6 text-2xl font-bold text-surface-900 dark:text-surface-50">Central de Comando</h1>
      <KanbanBoard />
    </DashboardLayout>
  );
}
