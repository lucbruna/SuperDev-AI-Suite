"use client";

import { useState } from "react";
import { api } from "@/utils/api-fetch";

type RefactorMode = "search-replace" | "rename" | "extract";

export function RefactorPanel() {
  const [mode, setMode] = useState<RefactorMode>("search-replace");
  const [filepath, setFilepath] = useState("");
  const [search, setSearch] = useState("");
  const [replace, setReplace] = useState("");
  const [oldName, setOldName] = useState("");
  const [newName, setNewName] = useState("");
  const [language, setLanguage] = useState("python");
  const [startLine, setStartLine] = useState("1");
  const [endLine, setEndLine] = useState("10");
  const [funcName, setFuncName] = useState("");
  const [result, setResult] = useState<any>(null);
  const [running, setRunning] = useState(false);

  const run = async () => {
    setRunning(true);
    setResult(null);
    try {
      let res;
      if (mode === "search-replace") {
        const data = await api.post<any>("/api/refactor/search-replace", { filepath, search, replace, dry_run: true });
        setResult(data);
      } else if (mode === "rename") {
        const data = await api.post<any>("/api/refactor/rename-symbol", { filepath, old_name: oldName, new_name: newName, language });
        setResult(data);
      } else {
        const data = await api.post<any>("/api/refactor/extract-function", { filepath, start_line: parseInt(startLine), end_line: parseInt(endLine), new_function_name: funcName });
        setResult(data);
      }
    } catch {}
    setRunning(false);
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        {(["search-replace", "rename", "extract"] as RefactorMode[]).map(m => (
          <button key={m} onClick={() => setMode(m)} className={`rounded-lg border px-3 py-1.5 text-[10px] font-medium ${mode === m ? "border-primary-500 bg-primary-50 dark:bg-primary-950" : "border-surface-300 dark:border-surface-600"}`}>{m === "search-replace" ? "Search & Replace" : m === "rename" ? "Rename Symbol" : "Extract Function"}</button>
        ))}
      </div>

      <div className="space-y-2">
        <input value={filepath} onChange={(e) => setFilepath(e.target.value)} placeholder="File path (e.g. src/app.ts)" className="w-full rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800" />

        {mode === "search-replace" && (
          <>
            <textarea value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Text to search..." rows={3} className="w-full rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs font-mono dark:border-surface-600 dark:bg-surface-800" />
            <textarea value={replace} onChange={(e) => setReplace(e.target.value)} placeholder="Replacement text..." rows={3} className="w-full rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs font-mono dark:border-surface-600 dark:bg-surface-800" />
          </>
        )}

        {mode === "rename" && (
          <div className="flex gap-2">
            <input value={oldName} onChange={(e) => setOldName(e.target.value)} placeholder="Old name..." className="flex-1 rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800" />
            <input value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="New name..." className="flex-1 rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800" />
            <select value={language} onChange={(e) => setLanguage(e.target.value)} className="rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800">
              {["python", "typescript", "javascript", "go", "rust"].map(l => <option key={l} value={l}>{l}</option>)}
            </select>
          </div>
        )}

        {mode === "extract" && (
          <div className="flex gap-2">
            <input value={startLine} onChange={(e) => setStartLine(e.target.value)} placeholder="Start line" className="w-20 rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800" />
            <input value={endLine} onChange={(e) => setEndLine(e.target.value)} placeholder="End line" className="w-20 rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800" />
            <input value={funcName} onChange={(e) => setFuncName(e.target.value)} placeholder="New function name..." className="flex-1 rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800" />
          </div>
        )}

        <button onClick={run} disabled={running || !filepath.trim()} className="w-full rounded-lg bg-primary-600 py-2 text-xs font-medium text-white hover:bg-primary-700 disabled:opacity-40">
          {running ? "Running..." : `Preview ${mode === "search-replace" ? "Search & Replace" : mode === "rename" ? "Rename" : "Extract"}`}
        </button>
      </div>

      {result && (
        <div className="rounded-xl border p-4 dark:border-surface-700">
          <p className="mb-1 text-xs font-semibold text-surface-900 dark:text-surface-50">
            {result.success ? "✅ Preview" : "❌ Error"}
          </p>
          <pre className="overflow-x-auto rounded bg-surface-50 p-2 text-[10px] dark:bg-surface-800 dark:text-surface-300">{JSON.stringify(result, null, 2)}</pre>
          {result.success && <button onClick={async () => { /* apply for real */ }} className="mt-2 rounded-lg bg-green-600 px-3 py-1.5 text-[10px] font-medium text-white hover:bg-green-700">Apply Changes</button>}
        </div>
      )}
    </div>
  );
}