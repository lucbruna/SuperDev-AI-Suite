"use client";

import { useState, useEffect } from "react";

interface SearchMatch {
  file: string;
  line: number;
  content: string;
  score: number;
}

export function SemanticSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchMatch[]>([]);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<"keyword" | "semantic">("keyword");

  useEffect(() => {
    if (!query.trim()) { setResults([]); return; }
    setLoading(true);
    const timer = setTimeout(() => {
      const q = query.toLowerCase();
      const mock: SearchMatch[] = [
        { file: "src/main.py", line: 12, content: "def main():", score: 95 },
        { file: "src/main.py", line: 45, content: "    result = process_data(args)", score: 80 },
        { file: "src/agent.py", line: 23, content: "class AgentRunner:", score: 75 },
        { file: "src/agent.py", line: 67, content: "    async def run(self):", score: 70 },
        { file: "src/utils.py", line: 8, content: "def process_data(input):", score: 65 },
      ].filter((m) => mode === "semantic" || m.content.toLowerCase().includes(q) || m.file.toLowerCase().includes(q));
      setResults(mock);
      setLoading(false);
    }, 300);
    return () => clearTimeout(timer);
  }, [query, mode]);

  return (
    <div className="rounded-xl border dark:border-surface-700">
      <div className="border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
        <div className="flex items-center gap-2">
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search codebase semantically..." autoFocus className="flex-1 rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100" />
          <div className="flex rounded-lg border dark:border-surface-600">
            <button onClick={() => setMode("keyword")} className={`px-2 py-1.5 text-[9px] ${mode === "keyword" ? "bg-primary-600 text-white" : "text-surface-500"}`}>Keyword</button>
            <button onClick={() => setMode("semantic")} className={`px-2 py-1.5 text-[9px] ${mode === "semantic" ? "bg-primary-600 text-white" : "text-surface-500"}`}>Semantic</button>
          </div>
        </div>
      </div>
      <div className="space-y-1 p-2">
        {loading ? (
          <div className="flex items-center justify-center py-4"><div className="h-4 w-4 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" /></div>
        ) : query && results.length === 0 ? (
          <p className="py-4 text-center text-xs text-surface-400">No results found</p>
        ) : (
          results.map((r, i) => (
            <button key={i} className="w-full rounded-lg px-3 py-2 text-left hover:bg-surface-50 dark:hover:bg-surface-800">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono text-primary-600">{r.file}:{r.line}</span>
                <span className="text-[9px] text-surface-400">{r.score}%</span>
              </div>
              <p className="text-[10px] text-surface-600 dark:text-surface-400">{r.content}</p>
            </button>
          ))
        )}
      </div>
    </div>
  );
}