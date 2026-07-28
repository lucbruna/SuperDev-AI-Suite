"use client";

import { useState } from "react";

const PROVIDER_PRESETS = [
  {
    name: "GitHub",
    description: "Manage repos, issues, PRs, and Actions",
    tools: [
      { name: "github.list_repos", description: "List user/organization repositories", endpoint: "/api/v1/github/repos" },
      { name: "github.create_issue", description: "Create a GitHub issue", endpoint: "/api/v1/github/issues" },
      { name: "github.list_prs", description: "List pull requests", endpoint: "/api/v1/github/pulls" },
    ],
  },
  {
    name: "Slack",
    description: "Send messages, list channels, manage threads",
    tools: [
      { name: "slack.send_message", description: "Send message to a channel", endpoint: "/api/v1/slack/message" },
      { name: "slack.list_channels", description: "List accessible channels", endpoint: "/api/v1/slack/channels" },
    ],
  },
  {
    name: "Database",
    description: "Query PostgreSQL, Redis, and more",
    tools: [
      { name: "db.query", description: "Execute a SQL query", endpoint: "/api/v1/db/query" },
      { name: "db.list_tables", description: "List database tables", endpoint: "/api/v1/db/tables" },
    ],
  },
  {
    name: "AI Models",
    description: "Invoke LLMs, embeddings, and completions",
    tools: [
      { name: "ai.chat", description: "Chat completion with any model", endpoint: "/api/v1/ai/chat" },
      { name: "ai.embed", description: "Generate embeddings", endpoint: "/api/v1/ai/embed" },
    ],
  },
];

export function MCPProviderConfig() {
  const [selected, setSelected] = useState<string[]>([]);

  const toggle = (name: string) => {
    setSelected((prev) =>
      prev.includes(name) ? prev.filter((n) => n !== name) : [...prev, name]
    );
  };

  const enableAll = () => setSelected(PROVIDER_PRESETS.map((p) => p.name));
  const disableAll = () => setSelected([]);

  return (
    <div className="rounded-xl border dark:border-surface-700">
      <div className="flex items-center justify-between border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
        <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">Provider Configuration</span>
        <div className="flex gap-1">
          <button onClick={enableAll} className="rounded bg-primary-600 px-2 py-1 text-[10px] text-white hover:bg-primary-700">All</button>
          <button onClick={disableAll} className="rounded bg-surface-300 px-2 py-1 text-[10px] text-surface-700 hover:bg-surface-400 dark:bg-surface-600 dark:text-surface-200">None</button>
        </div>
      </div>
      <div className="divide-y dark:divide-surface-700">
        {PROVIDER_PRESETS.map((provider) => (
          <div key={provider.name} className="p-3">
            <label className="flex cursor-pointer items-center gap-3">
              <input
                type="checkbox"
                checked={selected.includes(provider.name)}
                onChange={() => toggle(provider.name)}
                className="h-4 w-4 rounded border-surface-300 text-primary-600"
              />
              <div>
                <p className="text-sm font-medium text-surface-900 dark:text-surface-50">{provider.name}</p>
                <p className="text-xs text-surface-500">{provider.description}</p>
              </div>
              <span className="ml-auto text-[10px] text-surface-400">{provider.tools.length} tools</span>
            </label>
            {selected.includes(provider.name) && (
              <div className="ml-7 mt-2 space-y-1">
                {provider.tools.map((tool) => (
                  <div key={tool.name} className="flex items-center justify-between rounded bg-surface-50 px-2 py-1 dark:bg-surface-800">
                    <span className="text-[11px] font-mono text-surface-700 dark:text-surface-300">{tool.name}</span>
                    <span className="text-[10px] text-surface-500">{tool.endpoint}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}