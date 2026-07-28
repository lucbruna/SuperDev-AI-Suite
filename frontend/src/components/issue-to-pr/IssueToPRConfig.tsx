"use client";

import { useState } from "react";

const CONFIG_DEFAULTS = {
  auto_labels: ["pr-auto", "superdev", "ai", "auto-pr", "feature"],
  commands: ["/superdev", "/generate-pr", "/auto-pr"],
  branch_prefix: "auto/",
  create_draft_pr: true,
  assign_creator: true,
  add_issue_comment: true,
};

export function IssueToPRConfig() {
  const [config, setConfig] = useState(CONFIG_DEFAULTS);
  const [saved, setSaved] = useState(false);

  const toggle = (key: string) => {
    setConfig((prev) => ({ ...prev, [key]: !(prev as any)[key] }));
    setSaved(false);
  };

  const save = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="rounded-xl border dark:border-surface-700">
      <div className="border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
        <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">Configuration</span>
      </div>
      <div className="space-y-4 p-4">
        <div>
          <label className="text-xs font-medium text-surface-600">Auto-trigger labels</label>
          <div className="mt-1 flex flex-wrap gap-1">
            {config.auto_labels.map((label) => (
              <span key={label} className="rounded-full bg-primary-100 px-2 py-0.5 text-[10px] text-primary-700 dark:bg-primary-900 dark:text-primary-300">{label}</span>
            ))}
          </div>
        </div>
        <div>
          <label className="text-xs font-medium text-surface-600">Slash commands</label>
          <div className="mt-1 flex flex-wrap gap-1">
            {config.commands.map((cmd) => (
              <span key={cmd} className="rounded-full bg-surface-200 px-2 py-0.5 text-[10px] font-mono dark:bg-surface-700 dark:text-surface-300">{cmd}</span>
            ))}
          </div>
        </div>
        <div className="space-y-2">
          {[
            { key: "create_draft_pr", label: "Create as draft PR" },
            { key: "assign_creator", label: "Auto-assign issue creator" },
            { key: "add_issue_comment", label: "Add progress comment to issue" },
          ].map(({ key, label }) => (
            <label key={key} className="flex cursor-pointer items-center gap-2">
              <input type="checkbox" checked={(config as any)[key]} onChange={() => toggle(key)} className="h-4 w-4 rounded border-surface-300 text-primary-600" />
              <span className="text-xs text-surface-700 dark:text-surface-300">{label}</span>
            </label>
          ))}
        </div>
        <button onClick={save} className="w-full rounded-lg bg-primary-600 py-2 text-xs font-medium text-white hover:bg-primary-700">
          {saved ? "Saved!" : "Save Configuration"}
        </button>
      </div>
    </div>
  );
}