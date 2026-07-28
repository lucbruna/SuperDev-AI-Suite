"use client";

import { CloudVMPanel } from "../../components/cloud/CloudVMPanel";

export default function CloudPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-bold text-surface-900 dark:text-surface-50">Cloud Agent VMs</h1>
        <p className="text-sm text-surface-500">Provision and manage isolated cloud VMs for running agents with full browser + terminal access</p>
      </div>
      <CloudVMPanel />
    </div>
  );
}