"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/DashboardLayout";

interface MemoryEntry {
  id: string;
  content: string;
  type: string;
  created_at: string;
  relevance: number;
}

export default function MemoryPage() {
  const [entries, setEntries] = useState<MemoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetch("/api/v1/knowledge")
      .then((r) => r.json())
      .then((data) => {
        setEntries(Array.isArray(data) ? data : data?.knowledge || data?.data || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const filtered = entries.filter((e) =>
    e.content?.toLowerCase().includes(search.toLowerCase())
  );

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "code": return "📄";
      case "concept": return "💡";
      case "pattern": return "🔧";
      case "decision": return "📋";
      default: return "📌";
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-surface-900 dark:text-white">Memória</h1>
            <p className="text-surface-500">Contexto e conhecimento dos agentes</p>
          </div>
          <input
            type="text"
            placeholder="Buscar na memória..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800 w-64"
          />
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="rounded-lg border p-8 text-center dark:border-surface-700">
            <p className="text-surface-500">Nenhuma entrada encontrada</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filtered.map((entry) => (
              <div key={entry.id} className="rounded-lg border bg-white p-4 dark:border-surface-700 dark:bg-surface-900">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <span className="text-lg">{getTypeIcon(entry.type)}</span>
                    <div>
                      <p className="text-sm text-surface-900 dark:text-surface-100">{entry.content}</p>
                      <p className="mt-1 flex gap-3 text-[11px] text-surface-400">
                        <span>{entry.type}</span>
                        <span>{entry.created_at ? new Date(entry.created_at).toLocaleString() : "—"}</span>
                      </p>
                    </div>
                  </div>
                  {entry.relevance !== undefined && (
                    <span className="rounded-full bg-primary-100 px-2 py-0.5 text-[10px] text-primary-700 dark:bg-primary-900/30 dark:text-primary-300">
                      {(entry.relevance * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
