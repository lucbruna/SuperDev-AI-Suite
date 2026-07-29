"use client";

import { useState, useEffect } from "react";
import { api } from "@/utils/api-fetch";

export function DeployPanel() {
  const [env, setEnv] = useState("staging");
  const [version, setVersion] = useState("");
  const [strategy, setStrategy] = useState("rolling");
  const [deploying, setDeploying] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    api.get<any>("/api/deploy/history").then(d => setHistory(d.history || [])).catch(() => {});
  }, []);

  const doDeploy = async () => {
    if (!version.trim()) return;
    setDeploying(true);
    setResult(null);
    try {
      const data = await api.post<any>(`/api/deploy/deploy?env=${env}&version=${encodeURIComponent(version)}&strategy=${strategy}`);
      setResult(data);
      setHistory(prev => [data, ...prev].slice(0, 20));
    } catch {}
    setDeploying(false);
  };

  const doRollback = async () => {
    const data = await api.post<any>(`/api/deploy/rollback?env=${env}`);
    setResult(data);
  };

  const envColor = (e: string) => {
    const colors: Record<string, string> = { development: "bg-gray-500", staging: "bg-yellow-500", production: "bg-red-500" };
    return colors[e] || "bg-gray-400";
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-3">
        {["development", "staging", "production"].map(e => (
          <button key={e} onClick={() => setEnv(e)} className={`flex items-center gap-2 rounded-lg border px-4 py-2 text-xs font-medium ${env === e ? "border-primary-500 bg-primary-50 dark:bg-primary-950" : "border-surface-300 dark:border-surface-600"}`}>
            <span className={`h-2 w-2 rounded-full ${envColor(e)}`} />
            {e.charAt(0).toUpperCase() + e.slice(1)}
          </button>
        ))}
      </div>

      <div className="flex gap-2">
        <input value={version} onChange={(e) => setVersion(e.target.value)} onKeyDown={(e) => e.key === "Enter" && doDeploy()} placeholder="Version (e.g. v1.2.3)..." className="flex-1 rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800" />
        <select value={strategy} onChange={(e) => setStrategy(e.target.value)} className="rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100">
          <option value="rolling">Rolling</option>
          <option value="blue-green">Blue-Green</option>
          <option value="canary">Canary</option>
          <option value="recreate">Recreate</option>
        </select>
        <button onClick={doDeploy} disabled={deploying || !version.trim()} className="rounded-lg bg-primary-600 px-4 py-2 text-xs font-medium text-white hover:bg-primary-700 disabled:opacity-40">
          {deploying ? "Deploying..." : "Deploy"}
        </button>
        <button onClick={doRollback} className="rounded-lg bg-orange-600 px-4 py-2 text-xs font-medium text-white hover:bg-orange-700">Rollback</button>
      </div>

      {result && (
        <div className="rounded-xl border p-4 dark:border-surface-700">
          <p className="text-xs font-semibold text-surface-900 dark:text-surface-50">Result</p>
          <pre className="mt-1 overflow-x-auto rounded bg-surface-50 p-2 text-[10px] dark:bg-surface-800 dark:text-surface-300">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}

      {history.length > 0 && (
        <div className="rounded-xl border dark:border-surface-700">
          <div className="border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
            <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">Deploy History</span>
          </div>
          <div className="divide-y dark:divide-surface-700">
            {history.map((h: any, i: number) => (
              <div key={i} className="flex items-center justify-between px-4 py-2">
                <div className="flex items-center gap-2">
                  <span className={`h-2 w-2 rounded-full ${h.status === "completed" ? "bg-green-500" : "bg-red-500"}`} />
                  <span className="text-xs text-surface-700 dark:text-surface-200">{h.version || h.to_version || "-"}</span>
                  <span className="rounded bg-surface-100 px-1.5 py-0.5 text-[9px] text-surface-500 dark:bg-surface-700">{h.strategy || "-"}</span>
                </div>
                <span className="text-[10px] text-surface-400">{h.env} · {h.timestamp ? new Date(h.timestamp).toLocaleTimeString() : ""}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}