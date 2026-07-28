"use client";

import { useState } from "react";

const MODELS = [
  "gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet", "claude-3-haiku",
  "gemini-1.5-pro", "gemini-1.5-flash",
];

const DEFAULT_PROMPTS = ["Write a function to reverse a linked list", "Explain the CAP theorem", "Write a Python decorator for timing"];

export function EvalPanel() {
  const [modelA, setModelA] = useState(MODELS[0]);
  const [modelB, setModelB] = useState(MODELS[2]);
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const runEval = async () => {
    setLoading(true);
    setResults(null);
    try {
      const res = await fetch("/api/evals/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompts: DEFAULT_PROMPTS, model_a: modelA, model_b: modelB }),
      });
      setResults(await res.json());
    } catch (err: any) {
      setResults({ error: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-xl border dark:border-surface-700">
      <div className="border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
        <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">Side-by-Side Model Eval</span>
      </div>
      <div className="space-y-3 p-4">
        <div className="grid grid-cols-2 gap-2">
          <select value={modelA} onChange={(e) => setModelA(e.target.value)} className="rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100">
            {MODELS.map((m) => <option key={m} value={m}>{m}</option>)}
          </select>
          <select value={modelB} onChange={(e) => setModelB(e.target.value)} className="rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100">
            {MODELS.map((m) => <option key={m} value={m}>{m}</option>)}
          </select>
        </div>
        <button onClick={runEval} disabled={loading} className="w-full rounded-lg bg-primary-600 py-2 text-xs font-medium text-white hover:bg-primary-700 disabled:opacity-40">
          {loading ? "Running..." : "Run Comparison"}
        </button>
        {results && (
          <div className="space-y-2">
            <div className="flex items-center justify-between rounded-lg bg-green-950/30 p-3">
              <span className="text-xs font-medium text-green-400">Winner: {results.winner}</span>
              <span className="text-[10px] text-surface-500">{results.prompts_count} prompts</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div className="rounded-lg bg-surface-100 p-2 dark:bg-surface-800">
                <p className="text-[10px] font-medium text-surface-500">{modelA}</p>
                <p className="text-xs font-bold text-surface-900 dark:text-surface-50">{results.summary?.model_a?.wins} wins</p>
                <p className="text-[10px] text-surface-400">{results.summary?.model_a?.avg_duration_ms}ms avg</p>
              </div>
              <div className="rounded-lg bg-surface-100 p-2 dark:bg-surface-800">
                <p className="text-[10px] font-medium text-surface-500">{modelB}</p>
                <p className="text-xs font-bold text-surface-900 dark:text-surface-50">{results.summary?.model_b?.wins} wins</p>
                <p className="text-[10px] text-surface-400">{results.summary?.model_b?.avg_duration_ms}ms avg</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}