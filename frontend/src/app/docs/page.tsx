"use client";

import { useState } from "react";

export default function DocsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedModule, setSelectedModule] = useState<string | null>("src/main.py");
  const [activeTab, setActiveTab] = useState<"summary" | "modules" | "diagrams">("summary");

  const modules = [
    { path: "src/main.py", classes: ["App", "Config"], functions: ["main", "setup"], lines: 120 },
    { path: "src/utils.py", classes: ["Helper", "Formatter"], functions: ["parse", "validate"], lines: 85 },
    { path: "src/api.py", classes: ["Router", "Handler"], functions: ["get", "post", "delete"], lines: 200 },
    { path: "agents/base/base_agent.py", classes: ["BaseAgent"], functions: ["execute", "initialize"], lines: 150 },
  ];

  const docContent: Record<string, string> = {
    "src/main.py": "# src/main.py\n\n## Classes\n\n### `App`\nMain application entry point. Initializes routes and middleware.\n- `App(config: Config)` — constructor\n- `run()` — starts the server\n- `shutdown()` — graceful shutdown\n\n### `Config`\nApplication configuration loaded from environment.\n- `Config.from_env()` — load from environment variables\n- `debug: bool` — debug mode flag\n\n## Functions\n\n### `main()`\nEntry point. Creates App instance and runs it.",
    "src/utils.py": "# src/utils.py\n\n## Classes\n\n### `Helper`\nUtility helper functions for data processing.\n\n### `Formatter`\nOutput formatting utilities.\n\n## Functions\n\n### `parse(data: str) -> dict`\nParses JSON string into dictionary.\n\n### `validate(schema: dict, data: dict) -> bool`\nValidates data against a schema.",
  };

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-950">
      <header className="border-b bg-white dark:border-surface-700 dark:bg-surface-900">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <h1 className="text-xl font-bold text-primary-600">SuperDev</h1>
          <nav className="flex items-center gap-4">
            <a href="/dashboard" className="text-sm font-medium text-surface-600 hover:text-surface-900">Dashboard</a>
            <a href="/docs" className="text-sm font-medium text-primary-600">Docs</a>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-surface-900 dark:text-surface-50">Documentation</h2>
            <p className="mt-1 text-sm text-surface-600">Auto-generated from your codebase</p>
          </div>
          <div className="flex gap-3">
            <select className="rounded-lg border border-surface-300 bg-white px-3 py-2 text-sm">
              <option>All Modules</option>
              <option>Python</option>
              <option>TypeScript</option>
            </select>
            <button className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700">Regenerate</button>
          </div>
        </div>

        <div className="mt-4 flex gap-2">
          {(["summary", "modules", "diagrams"] as const).map((tab) => (
            <button key={tab} onClick={() => setActiveTab(tab)} className={`rounded-lg px-4 py-2 text-sm font-medium ${activeTab === tab ? "bg-primary-600 text-white" : "bg-surface-200 text-surface-600 hover:bg-surface-300 dark:bg-surface-700 dark:text-surface-400"}`}>
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
          <input
            type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} placeholder="Search documentation..."
            className="ml-auto rounded-lg border border-surface-300 bg-white px-4 py-2 text-sm focus:border-primary-500 focus:outline-none dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100"
          />
        </div>

        <div className="mt-6 grid grid-cols-4 gap-6">
          <div className="col-span-1">
            <div className="rounded-xl border bg-white p-3 dark:border-surface-700 dark:bg-surface-900">
              <h3 className="mb-2 text-xs font-semibold text-surface-500 uppercase">Modules</h3>
              {modules.map((m) => (
                <div key={m.path} onClick={() => setSelectedModule(m.path)} className={`cursor-pointer rounded px-2 py-1.5 text-xs ${selectedModule === m.path ? "bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300" : "text-surface-600 hover:bg-surface-100 dark:text-surface-400"}`}>
                  <p className="font-mono">{m.path}</p>
                  <p className="text-surface-400">{m.classes.length} classes, {m.functions.length} functions</p>
                </div>
              ))}
            </div>
          </div>

          <div className="col-span-3">
            <div className="rounded-xl border bg-white p-6 dark:border-surface-700 dark:bg-surface-900">
              {activeTab === "summary" && (
                <div>
                  <h3 className="text-lg font-bold text-surface-900 dark:text-surface-50">Project Summary</h3>
                  <div className="mt-4 grid grid-cols-4 gap-4">
                    {[{ label: "Modules", value: modules.length }, { label: "Classes", value: modules.reduce((s, m) => s + m.classes.length, 0) }, { label: "Functions", value: modules.reduce((s, m) => s + m.functions.length, 0) }, { label: "Lines of Code", value: modules.reduce((s, m) => s + m.lines, 0) }].map((s) => (
                      <div key={s.label} className="rounded-lg bg-surface-50 p-4 text-center dark:bg-surface-800">
                        <p className="text-2xl font-bold text-primary-600">{s.value}</p>
                        <p className="text-sm text-surface-500">{s.label}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === "modules" && selectedModule && (
                <pre className="whitespace-pre-wrap font-mono text-sm text-surface-700 dark:text-surface-300">{docContent[selectedModule] || "No documentation available for this module."}</pre>
              )}

              {activeTab === "diagrams" && (
                <div className="text-center text-surface-500">
                  <p className="text-lg">Class Diagram</p>
                  <pre className="mt-4 inline-block rounded-lg bg-surface-50 p-4 text-left font-mono text-xs dark:bg-surface-800">
                    {`┌─────────────┐     ┌──────────────┐
│  BaseAgent   │────>│  AgentRuntime │
└─────────────┘     └──────────────┘
       │
       v
┌──────────────┐
│  Executor    │
│  Reviewer    │
│  Deployer    │
└──────────────┘`}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}