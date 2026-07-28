"use client";

import { PromptHubPanel } from "../../components/prompt_hub/PromptHubPanel";

export default function PromptHubPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-bold text-surface-900 dark:text-surface-50">Prompt Hub</h1>
        <p className="text-sm text-surface-500">Version, diff, promote, and manage AI prompts across models</p>
      </div>
      <PromptHubPanel />
    </div>
  );
}