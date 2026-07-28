"use client";

import { useState } from "react";

interface Breakpoint {
  id: string;
  file: string;
  line: number;
  enabled: boolean;
  condition: string;
  hitCount: number;
}

interface StackFrame {
  id: string;
  function: string;
  file: string;
  line: number;
  locals: Record<string, string>;
}

export function DebuggerPanel() {
  const [breakpoints, setBreakpoints] = useState<Breakpoint[]>([
    { id: "bp1", file: "src/main.py", line: 42, enabled: true, condition: "x > 5", hitCount: 3 },
    { id: "bp2", file: "src/agent.py", line: 18, enabled: false, condition: "", hitCount: 0 },
  ]);
  const [stack] = useState<StackFrame[]>([
    { id: "f1", function: "process_data", file: "src/main.py", line: 42, locals: { x: "10", y: "'hello'", result: "None" } },
    { id: "f2", function: "main", file: "src/main.py", line: 55, locals: { args: "{name: 'test'}" } },
  ]);
  const [paused, setPaused] = useState(false);

  const toggleBreakpoint = (id: string) => {
    setBreakpoints((prev) => prev.map((bp) => bp.id === id ? { ...bp, enabled: !bp.enabled } : bp));
  };

  return (
    <div className="grid grid-cols-3 gap-4">
      <div className="rounded-xl border dark:border-surface-700">
        <div className="border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
          <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">Breakpoints ({breakpoints.length})</span>
        </div>
        <div className="space-y-1 p-2">
          {breakpoints.map((bp) => (
            <div key={bp.id} className={`flex items-center justify-between rounded-lg px-3 py-2 ${bp.enabled ? "bg-red-50 dark:bg-red-950/30" : "bg-surface-50 dark:bg-surface-800"}`}>
              <div>
                <p className="text-xs font-mono text-surface-700 dark:text-surface-300">{bp.file}:{bp.line}</p>
                {bp.condition && <p className="text-[9px] text-surface-500">if {bp.condition}</p>}
                <p className="text-[9px] text-surface-400">{bp.hitCount} hits</p>
              </div>
              <button onClick={() => toggleBreakpoint(bp.id)} className={`rounded px-1.5 py-0.5 text-[9px] ${bp.enabled ? "bg-red-600 text-white" : "bg-surface-300 text-surface-700 dark:bg-surface-600"}`}>
                {bp.enabled ? "Disable" : "Enable"}
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="col-span-2 rounded-xl border dark:border-surface-700">
        <div className="flex items-center justify-between border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
          <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">Stack Trace</span>
          <div className="flex gap-1">
            <button onClick={() => setPaused(!paused)} className={`rounded px-2 py-1 text-[9px] text-white ${paused ? "bg-green-600 hover:bg-green-700" : "bg-yellow-600 hover:bg-yellow-700"}`}>
              {paused ? "Resume" : "Pause"}
            </button>
            <button className="rounded bg-surface-300 px-2 py-1 text-[9px] text-surface-700 dark:bg-surface-600 dark:text-surface-300">Step Over</button>
            <button className="rounded bg-surface-300 px-2 py-1 text-[9px] text-surface-700 dark:bg-surface-600 dark:text-surface-300">Step Into</button>
            <button className="rounded bg-surface-300 px-2 py-1 text-[9px] text-surface-700 dark:bg-surface-600 dark:text-surface-300">Step Out</button>
          </div>
        </div>
        <div className="p-3">
          {paused && <div className="mb-2 rounded bg-yellow-100 px-3 py-1.5 text-[10px] text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">Paused at breakpoint bp1 (src/main.py:42)</div>}
          <div className="space-y-2">
            {stack.map((frame) => (
              <div key={frame.id} className="rounded-lg bg-surface-50 p-2 dark:bg-surface-800">
                <div className="flex items-center gap-2">
                  <span className="rounded bg-primary-100 px-1.5 py-0.5 text-[9px] font-mono text-primary-700 dark:bg-primary-900 dark:text-primary-300">{frame.function}</span>
                  <span className="text-[10px] text-surface-500">{frame.file}:{frame.line}</span>
                </div>
                <div className="mt-1 grid grid-cols-2 gap-1">
                  {Object.entries(frame.locals).map(([k, v]) => (
                    <div key={k} className="rounded bg-white px-2 py-0.5 text-[9px] font-mono dark:bg-surface-900">
                      <span className="text-primary-500">{k}</span> = <span className="text-surface-600 dark:text-surface-400">{v}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}