"use client";

import { useState } from "react";

interface CallResult {
  tool_call_id: string;
  tool_name: string;
  result: any;
  error: string | null;
  duration_ms: number;
}

export function MCPConsole() {
  const [toolName, setToolName] = useState("");
  const [args, setArgs] = useState("{}");
  const [result, setResult] = useState<CallResult | null>(null);
  const [loading, setLoading] = useState(false);

  const call = async () => {
    setLoading(true);
    setResult(null);
    try {
      let parsed = {};
      try { parsed = JSON.parse(args); } catch {}
      const res = await fetch("/api/mcp/call", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tool_name: toolName, arguments: parsed }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setResult({
        tool_call_id: "error",
        tool_name: toolName,
        result: null,
        error: err.message,
        duration_ms: 0,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-xl border dark:border-surface-700">
      <div className="border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
        <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">MCP Console</span>
      </div>
      <div className="space-y-3 p-4">
        <input
          value={toolName}
          onChange={(e) => setToolName(e.target.value)}
          placeholder="Tool name"
          className="w-full rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100"
        />
        <textarea
          value={args}
          onChange={(e) => setArgs(e.target.value)}
          rows={4}
          placeholder='{"key": "value"}'
          className="w-full rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs font-mono dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100"
        />
        <button
          onClick={call}
          disabled={loading || !toolName.trim()}
          className="w-full rounded-lg bg-primary-600 py-2 text-xs font-medium text-white hover:bg-primary-700 disabled:opacity-40"
        >
          {loading ? "Calling..." : "Call Tool"}
        </button>
        {result && (
          <div className={`rounded-lg p-3 ${result.error ? "bg-red-950/30" : "bg-green-950/30"}`}>
            <div className="flex items-center justify-between">
              <span className={`text-xs font-medium ${result.error ? "text-red-400" : "text-green-400"}`}>
                {result.error ? "Error" : "Success"} — {result.duration_ms}ms
              </span>
              <span className="text-[10px] text-surface-500">{result.tool_call_id}</span>
            </div>
            <pre className="mt-2 overflow-x-auto text-[10px] text-surface-600 dark:text-surface-400">
              {JSON.stringify(result.error || result.result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}