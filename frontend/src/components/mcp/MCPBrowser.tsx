"use client";

import { useState, useEffect } from "react";

interface MCPTool {
  name: string;
  description: string;
  input_schema: Record<string, any>;
}

export function MCPBrowser() {
  const [tools, setTools] = useState<MCPTool[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [selectedTool, setSelectedTool] = useState<MCPTool | null>(null);

  useEffect(() => {
    fetch("/api/mcp/tools")
      .then((r) => r.json())
      .then(setTools)
      .catch(() => setTools([]))
      .finally(() => setLoading(false));
  }, []);

  const filtered = tools.filter(
    (t) =>
      t.name.toLowerCase().includes(search.toLowerCase()) ||
      t.description.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="rounded-xl border dark:border-surface-700">
      <div className="border-b bg-surface-50 px-4 py-3 dark:border-surface-700 dark:bg-surface-800">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-surface-900 dark:text-surface-50">MCP Tools ({tools.length})</h2>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search tools..."
            className="w-48 rounded-lg border border-surface-300 bg-white px-3 py-1.5 text-xs dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100"
          />
        </div>
      </div>
      {loading ? (
        <div className="flex items-center justify-center p-8">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="p-8 text-center text-sm text-surface-400">
          {search ? "No tools match your search" : "No MCP tools registered. Register a tool to get started."}
        </div>
      ) : (
        <div className="divide-y dark:divide-surface-700">
          {filtered.map((tool) => (
            <button
              key={tool.name}
              onClick={() => setSelectedTool(selectedTool?.name === tool.name ? null : tool)}
              className="w-full px-4 py-3 text-left hover:bg-surface-50 dark:hover:bg-surface-800"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-surface-900 dark:text-surface-50">{tool.name}</span>
                <span className="rounded-full bg-primary-100 px-2 py-0.5 text-[10px] font-medium text-primary-700 dark:bg-primary-900 dark:text-primary-300">
                  {Object.keys(tool.input_schema?.properties || {}).length} params
                </span>
              </div>
              <p className="mt-0.5 text-xs text-surface-500">{tool.description}</p>
              {selectedTool?.name === tool.name && (
                <div className="mt-2 rounded-lg bg-surface-100 p-3 dark:bg-surface-800">
                  <p className="mb-1 text-[10px] font-semibold uppercase text-surface-500">Input Schema</p>
                  <pre className="overflow-x-auto text-[10px] text-surface-600 dark:text-surface-400">
                    {JSON.stringify(tool.input_schema, null, 2)}
                  </pre>
                </div>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}