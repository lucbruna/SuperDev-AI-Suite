"use client";

import { useState } from "react";

interface MemoryEntry {
  key: string;
  value: string;
  namespace: string;
  updatedAt: string;
  similarity?: number;
}

export default function MemoryPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [namespace, setNamespace] = useState("default");
  const [entries, setEntries] = useState<MemoryEntry[]>([
    { key: "session:abc123", value: "Architect Agent - Designed microservices architecture for project X", namespace: "default", updatedAt: "2026-07-28T10:00:00Z" },
    { key: "session:def456", value: "Executor Agent - Deployed workflow pipeline to staging", namespace: "default", updatedAt: "2026-07-27T15:30:00Z" },
    { key: "pref:theme", value: "dark", namespace: "user:1", updatedAt: "2026-07-26T08:00:00Z" },
    { key: "pref:model", value: "gpt-4o", namespace: "user:1", updatedAt: "2026-07-26T08:00:00Z" },
  ]);
  const [filtered, setFiltered] = useState<MemoryEntry[]>([]);
  const [viewMode, setViewMode] = useState<"cards" | "table">("cards");

  const handleSearch = () => {
    if (!searchQuery.trim()) {
      setFiltered([]);
      return;
    }
    const q = searchQuery.toLowerCase();
    setFiltered(entries.filter((e) => e.key.toLowerCase().includes(q) || e.value.toLowerCase().includes(q)));
  };

  const displayEntries = filtered.length > 0 ? filtered : entries;

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-950">
      <header className="border-b bg-white dark:border-surface-700 dark:bg-surface-900">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <h1 className="text-xl font-bold text-primary-600">SuperDev</h1>
          <nav className="flex items-center gap-4">
            <a href="/dashboard" className="text-sm font-medium text-surface-600 hover:text-surface-900 dark:text-surface-400">Dashboard</a>
            <a href="/agents" className="text-sm font-medium text-surface-600 hover:text-surface-900 dark:text-surface-400">Agentes</a>
            <a href="/memory" className="text-sm font-medium text-primary-600">Memória</a>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-surface-900 dark:text-surface-50">Memórias dos Agentes</h2>
            <p className="mt-1 text-sm text-surface-600 dark:text-surface-400">Contexto persistente entre sessões de agentes</p>
          </div>
          <div className="flex gap-2">
            <button onClick={() => setViewMode("cards")} className={`rounded-lg px-3 py-1.5 text-sm ${viewMode === "cards" ? "bg-primary-600 text-white" : "bg-surface-200 text-surface-700 dark:bg-surface-700 dark:text-surface-300"}`}>Cards</button>
            <button onClick={() => setViewMode("table")} className={`rounded-lg px-3 py-1.5 text-sm ${viewMode === "table" ? "bg-primary-600 text-white" : "bg-surface-200 text-surface-700 dark:bg-surface-700 dark:text-surface-300"}`}>Tabela</button>
          </div>
        </div>

        <div className="mt-6 flex gap-3">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder="Buscar em memórias..."
            className="flex-1 rounded-lg border border-surface-300 bg-white px-4 py-2 text-sm focus:border-primary-500 focus:outline-none dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100"
          />
          <select
            value={namespace}
            onChange={(e) => setNamespace(e.target.value)}
            className="rounded-lg border border-surface-300 bg-white px-3 py-2 text-sm dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100"
          >
            <option value="default">default</option>
            <option value="user:1">user:1</option>
            <option value="session">session</option>
          </select>
          <button onClick={handleSearch} className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700">Buscar</button>
        </div>

        <div className="mt-2 flex items-center gap-2 text-xs text-surface-500">
          <span>{displayEntries.length} entradas</span>
          <span>|</span>
          <span>Namespace: {namespace}</span>
        </div>

        {viewMode === "cards" ? (
          <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {displayEntries.map((entry) => (
              <div key={entry.key} className="rounded-xl border bg-white p-4 shadow-sm dark:border-surface-700 dark:bg-surface-900">
                <div className="flex items-start justify-between">
                  <span className="rounded bg-primary-100 px-2 py-0.5 text-xs font-medium text-primary-700 dark:bg-primary-900 dark:text-primary-300">{entry.namespace}</span>
                  {entry.similarity !== undefined && (
                    <span className="text-xs text-green-600">{(entry.similarity * 100).toFixed(0)}% match</span>
                  )}
                </div>
                <p className="mt-2 text-xs font-mono text-surface-500">{entry.key}</p>
                <p className="mt-1 text-sm text-surface-700 dark:text-surface-300">{entry.value}</p>
                <p className="mt-2 text-xs text-surface-400">{new Date(entry.updatedAt).toLocaleString()}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="mt-4 overflow-x-auto rounded-xl border bg-white dark:border-surface-700 dark:bg-surface-900">
            <table className="w-full text-left text-sm">
              <thead className="border-b bg-surface-50 dark:border-surface-700 dark:bg-surface-800">
                <tr>
                  <th className="px-4 py-3 font-medium text-surface-600 dark:text-surface-400">Key</th>
                  <th className="px-4 py-3 font-medium text-surface-600 dark:text-surface-400">Value</th>
                  <th className="px-4 py-3 font-medium text-surface-600 dark:text-surface-400">Namespace</th>
                  <th className="px-4 py-3 font-medium text-surface-600 dark:text-surface-400">Updated</th>
                </tr>
              </thead>
              <tbody className="divide-y dark:divide-surface-700">
                {displayEntries.map((entry) => (
                  <tr key={entry.key} className="hover:bg-surface-50 dark:hover:bg-surface-800/50">
                    <td className="px-4 py-3 font-mono text-xs text-surface-700 dark:text-surface-300">{entry.key}</td>
                    <td className="px-4 py-3 text-surface-700 dark:text-surface-300">{entry.value}</td>
                    <td className="px-4 py-3"><span className="rounded bg-surface-100 px-2 py-0.5 text-xs dark:bg-surface-700">{entry.namespace}</span></td>
                    <td className="px-4 py-3 text-xs text-surface-400">{new Date(entry.updatedAt).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}