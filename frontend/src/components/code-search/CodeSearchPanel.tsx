"use client";

import { useState, useEffect, useCallback } from "react";

interface SearchMatch {
  line: number;
  content: string;
}

interface SearchResult {
  file: string;
  ext: string;
  total_lines: number;
  matches_count: number;
  matches: SearchMatch[];
  score: number;
}

interface SearchResponse {
  query: string;
  total_results: number;
  total_files_searched: number;
  results: SearchResult[];
  file_filters: string[];
}

const API_BASE = "/api/code-search";

export function CodeSearchPanel() {
  const [query, setQuery] = useState("");
  const [extFilter, setExtFilter] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [totalResults, setTotalResults] = useState(0);
  const [fileFilters, setFileFilters] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState("");
  const [stats, setStats] = useState<{ total_files: number; total_lines: number } | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/stats`)
      .then((r) => r.json())
      .then(setStats)
      .catch(() => {});
  }, []);

  const search = useCallback(async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const params = new URLSearchParams({ q: query, max_results: "30" });
      if (extFilter) params.set("ext", extFilter);
      const res = await fetch(`${API_BASE}/search?${params}`);
      const data: SearchResponse = await res.json();
      setResults(data.results);
      setTotalResults(data.total_results);
      setFileFilters(data.file_filters);
    } catch {
      setResults([]);
      setTotalResults(0);
    } finally {
      setLoading(false);
    }
  }, [query, extFilter]);

  const openFile = async (filepath: string) => {
    setSelectedFile(filepath);
    try {
      const res = await fetch(`${API_BASE}/file/${filepath}`);
      const data = await res.json();
      setFileContent(data.content);
    } catch {
      setFileContent("// Error loading file");
    }
  };

  return (
    <div className="flex h-[calc(100vh-80px)] gap-4">
      <div className="flex w-2/5 flex-col rounded-xl border dark:border-surface-700">
        <div className="border-b bg-surface-50 px-4 py-3 dark:border-surface-700 dark:bg-surface-800">
          <div className="flex gap-2">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && search()}
              placeholder="Search codebase in natural language..."
              className="flex-1 rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100"
            />
            <select value={extFilter} onChange={(e) => setExtFilter(e.target.value)} className="w-20 rounded-lg border border-surface-300 bg-white px-2 py-2 text-xs dark:border-surface-600 dark:bg-surface-800">
              <option value="">All</option>
              {fileFilters.map((f) => <option key={f} value={f}>{f}</option>)}
            </select>
            <button onClick={search} disabled={loading || !query.trim()} className="rounded-lg bg-primary-600 px-4 py-2 text-xs font-medium text-white hover:bg-primary-700 disabled:opacity-40">
              {loading ? "..." : "Search"}
            </button>
          </div>
          {stats && (
            <p className="mt-1.5 text-[10px] text-surface-500">{stats.total_files} files · {stats.total_lines.toLocaleString()} lines indexed</p>
          )}
        </div>
        <div className="flex-1 overflow-y-auto divide-y dark:divide-surface-700">
          {totalResults === 0 && !loading && query && (
            <div className="flex items-center justify-center p-8 text-xs text-surface-400">No results for "{query}"</div>
          )}
          {results.map((r) => (
            <button key={r.file} onClick={() => openFile(r.file)} className={`w-full px-4 py-3 text-left hover:bg-surface-50 dark:hover:bg-surface-800 ${selectedFile === r.file ? "bg-primary-50 dark:bg-primary-900/20" : ""}`}>
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-surface-900 dark:text-surface-50">{r.file}</span>
                <span className="text-[10px] text-surface-400">{r.matches_count} matches</span>
              </div>
              <div className="mt-1 space-y-0.5">
                {r.matches.slice(0, 3).map((m, i) => (
                  <div key={i} className="rounded bg-surface-100 px-2 py-0.5 text-[10px] font-mono text-surface-600 dark:bg-surface-800 dark:text-surface-400">
                    <span className="text-surface-400">L{m.line}: </span>
                    {m.content}
                  </div>
                ))}
              </div>
            </button>
          ))}
        </div>
      </div>
      <div className="flex-1 rounded-xl border dark:border-surface-700 overflow-hidden">
        <div className="border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
          <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">{selectedFile || "Select a file to preview"}</span>
        </div>
        <pre className="h-full overflow-auto p-4 text-xs font-mono text-surface-700 dark:text-surface-300">
          {selectedFile ? fileContent.slice(0, 10000) : "Click a search result to preview the file content"}
        </pre>
      </div>
    </div>
  );
}