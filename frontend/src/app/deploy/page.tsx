"use client";

import { DeployPanel } from "../../components/deploy/DeployPanel";

export default function DeployPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-bold text-surface-900 dark:text-surface-50">Auto-Deploy</h1>
        <p className="text-sm text-surface-500">Deploy to development, staging, or production with rolling, blue-green, canary, or recreate strategies</p>
      </div>
      <DeployPanel />
    </div>
  );
}