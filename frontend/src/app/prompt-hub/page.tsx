"use client";

import { DashboardLayout } from "@/components/DashboardLayout";
import { PromptHubPanel } from "@/components/prompt_hub/PromptHubPanel";

export default function PromptHubPage() {
  return (
    <DashboardLayout>
      <h1 className="mb-6 text-2xl font-bold text-surface-900 dark:text-surface-50">Prompt Hub</h1>
      <PromptHubPanel />
    </DashboardLayout>
  );
}
