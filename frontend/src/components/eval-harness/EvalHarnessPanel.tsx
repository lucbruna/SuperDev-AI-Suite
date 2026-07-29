"use client";

import { useState, useEffect } from "react";
import { api } from "@/utils/api-fetch";

const DEFAULT_TESTS = [
  { name: "factual_accuracy", description: "Knowledge recall test" },
  { name: "code_generation", description: "Code output correctness" },
  { name: "summarization", description: "Minimum response length" },
  { name: "safety", description: "Refusal of harmful requests" },
  { name: "reasoning", description: "Logical deduction chains" },
];

export function EvalHarnessPanel() {
  const [model, setModel] = useState("gpt-4o");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [selectedTests, setSelectedTests] = useState<string[]>(DEFAULT_TESTS.map((t) => t.name));

  useEffect(() => {
    api.get<any>("/eval-harness/runs").then((d) => setHistory(d.runs || [])).catch(() => {});
  }, []);

  const toggleTest = (name: string) => {
    setSelectedTests((prev) => prev.includes(name) ? prev.filter((n) => n !== name) : [...prev, name]);
  };

  const run = async () => {
    setRunning(true);
    setResult(null);
    try {
      const data = await api.post<any>(`/eval-harness/run?model=${model}`);
      setResult(data);
      setHistory((prev) => [data, ...prev]);
    } catch (err: any) {
      setResult({ error: err.message });
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="grid grid-cols-3 gap-4">
      <div className="rounded-xl border dark:border-surface-700">
        <div className="border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
          <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">Test Selection</span>
        </div>
        <div className="space-y-2 p-3">
          <select value={model} onChange={(e) => setModel(e.target.value)} className="w-full rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800">
            {["gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet", "claude-3-haiku", "gemini-1.5-pro", "gemini-1.5-flash"].map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
          <div className="space-y-1">
            {DEFAULT_TESTS.map((t) => (
              <label key={t.name} className="flex cursor-pointer items-center gap-2 rounded-lg bg-surface-50 px-2 py-1.5 dark:bg-surface-800">
                <input type="checkbox" checked={selectedTests.includes(t.name)} onChange={() => toggleTest(t.name)} className="h-3 w-3 rounded border-surface-300 text-primary-600" />
                <div>
                  <p className="text-[10px] font-medium text-surface-700 dark:text-surface-300">{t.name}</p>
                  <p className="text-[9px] text-surface-500">{t.description}</p>
                </div>
              </label>
            ))}
          </div>
          <button onClick={run} disabled={running || selectedTests.length === 0} className="w-full rounded-lg bg-primary-600 py-2 text-xs font-medium text-white hover:bg-primary-700 disabled:opacity-40">
            {running ? "Running..." : `Run ${selectedTests.length} Tests`}
          </button>
        </div>
      </div>

      <div className="rounded-xl border dark:border-surface-700">
        <div className="border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
          <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">Results</span>
        </div>
        <div className="space-y-2 p-3">
          {result ? (
            <>
              <div className="flex items-center gap-4 rounded-lg bg-green-950/30 p-3">
                <div className="text-center">
                  <p className="text-lg font-bold text-green-400">{result.accuracy}%</p>
                  <p className="text-[10px] text-green-600">accuracy</p>
                </div>
                <div>
                  <p className="text-xs text-surface-300">{result.passed}/{result.total_tests} passed</p>
                  <p className="text-[10px] text-surface-500">{result.avg_duration_ms}ms avg · {result.model}</p>
                </div>
              </div>
              <div className="space-y-1">
                {(result.results || []).map((r: any, i: number) => (
                  <div key={i} className={`flex items-center justify-between rounded-lg px-3 py-2 ${r.passed ? "bg-green-950/20" : "bg-red-950/20"}`}>
                    <span className="text-[10px] font-medium text-surface-300">{r.name}</span>
                    <span className={`text-[9px] ${r.passed ? "text-green-500" : "text-red-500"}`}>{r.passed ? "PASS" : "FAIL"}</span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <p className="py-8 text-center text-xs text-surface-400">Run tests to see results</p>
          )}
        </div>
      </div>

      <div className="rounded-xl border dark:border-surface-700">
        <div className="border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
          <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">History</span>
        </div>
        <div className="max-h-80 space-y-1 overflow-y-auto p-2">
          {history.slice(0, 15).map((r: any) => (
            <div key={r.id} className="rounded bg-surface-50 px-2 py-1.5 dark:bg-surface-800">
              <div className="flex items-center justify-between">
                <span className="text-[9px] font-mono text-surface-500">{r.model}</span>
                <span className={`text-[9px] font-medium ${r.accuracy >= 80 ? "text-green-500" : r.accuracy >= 50 ? "text-yellow-500" : "text-red-500"}`}>{r.accuracy}%</span>
              </div>
              <p className="text-[9px] text-surface-400">{r.passed}/{r.total_tests} · {r.avg_duration_ms}ms</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}