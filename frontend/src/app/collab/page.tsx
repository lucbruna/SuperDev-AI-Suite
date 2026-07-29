"use client";

import { DashboardLayout } from "@/components/DashboardLayout";
import { CollaborativeEditor } from "@/components/editor/CollaborativeEditor";

export default function CollabPage() {
  return (
    <DashboardLayout>
      <h1 className="mb-6 text-2xl font-bold text-surface-900 dark:text-surface-50">Colaboração</h1>
      <CollaborativeEditor />
    </DashboardLayout>
  );
}
