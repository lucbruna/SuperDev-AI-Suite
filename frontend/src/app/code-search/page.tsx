"use client";

import { DashboardLayout } from "@/components/DashboardLayout";
import { CodeSearchPanel } from "@/components/code-search/CodeSearchPanel";

export default function CodeSearchPage() {
  return (
    <DashboardLayout>
      <h1 className="mb-6 text-2xl font-bold text-surface-900 dark:text-surface-50">Busca de Código</h1>
      <CodeSearchPanel />
    </DashboardLayout>
  );
}
