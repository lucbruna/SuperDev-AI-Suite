"use client";

import { DashboardLayout } from "@/components/DashboardLayout";
import { CloudVMPanel } from "@/components/cloud/CloudVMPanel";

export default function CloudPage() {
  return (
    <DashboardLayout>
      <h1 className="mb-6 text-2xl font-bold text-surface-900 dark:text-surface-50">Cloud</h1>
      <CloudVMPanel />
    </DashboardLayout>
  );
}
