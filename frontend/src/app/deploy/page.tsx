"use client";

import { DashboardLayout } from "@/components/DashboardLayout";
import { DeployPanel } from "@/components/deploy/DeployPanel";

export default function DeployPage() {
  return (
    <DashboardLayout>
      <h1 className="mb-6 text-2xl font-bold text-surface-900 dark:text-surface-50">Deploy</h1>
      <DeployPanel />
    </DashboardLayout>
  );
}
