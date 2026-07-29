"use client";

import { DashboardLayout } from "@/components/DashboardLayout";
import { IssueToPR } from "@/components/issue-to-pr/IssueToPR";

export default function IssueToPRPage() {
  return (
    <DashboardLayout>
      <h1 className="mb-6 text-2xl font-bold text-surface-900 dark:text-surface-50">Issue to PR</h1>
      <IssueToPR />
    </DashboardLayout>
  );
}
