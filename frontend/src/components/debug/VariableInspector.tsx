"use client";

import { useState } from "react";

interface WatchExpression {
  id: string;
  expression: string;
  value: string;
  type: string;
}

export function VariableInspector() {
  const [scope] = useState<"local" | "global" | "closure">("local");
  const [watchExpr, setWatchExpr] = useState("");
  const [watches, setWatches] = useState<WatchExpression[]>([
    { id: "w1", expression: "x", value: "10", type: "int" },
    { id: "w2", expression: "y", value: "'hello'", type: "str" },
    { id: "w3", expression: "result", value: "None", type: "NoneType" },
    { id: "w4", expression: "items", value: "[1, 2, 3, 4, 5]", type: "list" },
  ]);

  const addWatch = () => {
    if (!watchExpr.trim()) return;
    setWatches((prev) => [...prev, { id: `w${Date.now()}`, expression: watchExpr, value: "undefined", type: "unknown" }]);
    setWatchExpr("");
  };

  const removeWatch = (id: string) => {
    setWatches((prev) => prev.filter((w) => w.id !== id));
  };

  return (
    <div className="rounded-xl border dark:border-surface-700">
      <div className="flex items-center justify-between border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
        <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">Variable Inspector</span>
        <div className="flex gap-1">
          {(["local", "global", "closure"] as const).map((s) => (
            <button key={s} onClick={() => {}} className={`rounded px-2 py-0.5 text-[9px] ${scope === s ? "bg-primary-600 text-white" : "bg-surface-200 text-surface-600 dark:bg-surface-700"}`}>
              {s}
            </button>
          ))}
        </div>
      </div>
      <div className="space-y-2 p-3">
        <div className="flex gap-1">
          <input value={watchExpr} onChange={(e) => setWatchExpr(e.target.value)} onKeyDown={(e) => e.key === "Enter" && addWatch()} placeholder="Add watch expression..." className="flex-1 rounded-lg border border-surface-300 bg-white px-2 py-1.5 text-[10px] font-mono dark:border-surface-600 dark:bg-surface-800" />
          <button onClick={addWatch} className="rounded bg-primary-600 px-2 py-1 text-[9px] text-white hover:bg-primary-700">+</button>
        </div>
        <div className="divide-y dark:divide-surface-700">
          {watches.map((w) => (
            <div key={w.id} className="flex items-center justify-between py-1.5">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-primary-500">{w.expression}</span>
                <span className="text-[9px] text-surface-400">=</span>
                <span className="text-xs font-mono text-surface-700 dark:text-surface-300">{w.value}</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="rounded bg-surface-200 px-1.5 py-0.5 text-[8px] text-surface-500 dark:bg-surface-700">{w.type}</span>
                <button onClick={() => removeWatch(w.id)} className="text-[9px] text-red-400 hover:text-red-600">✕</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}