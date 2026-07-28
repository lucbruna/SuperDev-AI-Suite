"use client";

import { CustomInstructionsPanel } from "../../components/configuration/CustomInstructionsPanel";

export default function InstructionsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-bold text-surface-900 dark:text-surface-50">Custom Instructions</h1>
        <p className="text-sm text-surface-500">Define per-file-pattern rules that tell AI agents how to write code in your project</p>
      </div>
      <CustomInstructionsPanel />
    </div>
  );
}