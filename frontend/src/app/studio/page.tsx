"use client";

import { useState, useEffect, useRef, useCallback } from "react";

interface GraphNode {
  id: string;
  label: string;
  status: "pending" | "running" | "completed" | "error" | "paused";
  type: string;
}

interface Breakpoint {
  id: string;
  nodeId: string;
  enabled: boolean;
  hitCount: number;
}

interface LogEntry {
  time: string;
  level: string;
  message: string;
}

const WS_BASE = "ws://localhost:8000/studio/ws";

export default function StudioPage() {
  const [activeTab, setActiveTab] = useState<"graph" | "inspector" | "console" | "breakpoints">("graph");
  const [isRunning, setIsRunning] = useState(false);
  const [stepMode, setStepMode] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [connected, setConnected] = useState(false);

  const [nodes, setNodes] = useState<GraphNode[]>([
    { id: "n1", label: "Input", status: "pending", type: "input" },
    { id: "n2", label: "Analyze", status: "pending", type: "process" },
    { id: "n3", label: "Transform", status: "pending", type: "process" },
    { id: "n4", label: "Validate", status: "pending", type: "process" },
    { id: "n5", label: "Output", status: "pending", type: "output" },
  ]);

  const [breakpoints, setBreakpoints] = useState<Breakpoint[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([
    { time: new Date().toLocaleTimeString(), level: "info", message: "Studio initialized" },
  ]);
  const [variables, setVariables] = useState<Record<string, any>>({});

  const wsRef = useRef<WebSocket | null>(null);

  const addLog = useCallback((level: string, message: string) => {
    setLogs((prev) => [...prev, { time: new Date().toLocaleTimeString(), level, message }]);
  }, []);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    const ws = new WebSocket(`${WS_BASE}?session_id=${sessionId || "default"}`);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      addLog("info", "WebSocket connected");
      ws.send(JSON.stringify({ type: "session:create", project_id: "default" }));
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        const type = msg.type;

        if (type === "session:created") {
          setSessionId(msg.session_id);
          addLog("info", `Session created: ${msg.session_id}`);
          ws.send(JSON.stringify({ type: "get:state", session_id: msg.session_id }));
        }

        if (type === "state:snapshot") {
          if (msg.graph) setNodes((prev) => prev.map((n) => ({ ...n, status: (msg.graph as any)?.[n.id]?.status || n.status })));
          if (msg.variables) setVariables(msg.variables);
          if (msg.breakpoints) setBreakpoints(msg.breakpoints.map((bp: any) => ({ id: bp.id || bp.breakpoint_id, nodeId: bp.node_id || "", enabled: bp.enabled ?? true, hitCount: bp.hit_count || 0 })));
        }

        if (type === "STUDIO_NODE_START" || type.endsWith("NODE_START")) {
          setNodes((prev) => prev.map((n) => (n.id === msg.payload?.node_id ? { ...n, status: "running" } : n)));
          addLog("info", `Node ${msg.payload?.node_id} started`);
        }

        if (type === "STUDIO_NODE_END" || type.endsWith("NODE_END")) {
          setNodes((prev) => prev.map((n) => (n.id === msg.payload?.node_id ? { ...n, status: "completed" } : n)));
          addLog("info", `Node ${msg.payload?.node_id} completed`);
        }

        if (type === "STUDIO_BREAKPOINT_HIT" || type.endsWith("BREAKPOINT_HIT")) {
          addLog("warn", `Breakpoint hit at node ${msg.payload?.node_id}`);
          setBreakpoints((prev) => prev.map((bp) => (bp.nodeId === msg.payload?.node_id ? { ...bp, hitCount: bp.hitCount + 1 } : bp)));
        }

        if (type === "STUDIO_STEP_COMPLETE") {
          addLog("info", `Step ${msg.payload?.action || "complete"}`);
        }

        if (type === "STUDIO_VARIABLE_CHANGE") {
          setVariables((prev) => ({ ...prev, ...msg.payload?.variables }));
        }

        if (type === "session:stopped") {
          setIsRunning(false);
          addLog("info", "Session stopped");
        }

        if (type === "breakpoint:set" && msg.breakpoint) {
          setBreakpoints((prev) => [...prev.filter((b) => b.nodeId !== msg.breakpoint.node_id), { id: msg.breakpoint.id || msg.breakpoint.breakpoint_id, nodeId: msg.breakpoint.node_id, enabled: true, hitCount: 0 }]);
        }

        if (type === "breakpoint:removed") {
          setBreakpoints((prev) => prev.filter((b) => b.id !== msg.breakpoint_id));
        }
      } catch {}
    };

    ws.onclose = () => {
      setConnected(false);
      addLog("warn", "WebSocket disconnected");
    };

    ws.onerror = () => {
      addLog("error", "WebSocket error");
    };
  }, [sessionId, addLog]);

  useEffect(() => {
    connect();
    return () => { wsRef.current?.close(); };
  }, [connect]);

  const send = useCallback((msg: Record<string, any>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(msg));
    }
  }, []);

  const handleRun = () => {
    if (isRunning) {
      send({ type: "session:stop", session_id: sessionId });
      setIsRunning(false);
    } else {
      if (!sessionId) {
        send({ type: "session:create", project_id: "default" });
      }
      setIsRunning(true);
      addLog("info", "Execution started");
    }
  };

  const handleStep = (action: string) => {
    send({ type: `step:${action}`, session_id: sessionId });
  };

  const toggleBreakpoint = (nodeId: string) => {
    const existing = breakpoints.find((b) => b.nodeId === nodeId);
    if (existing) {
      send({ type: "breakpoint:remove", session_id: sessionId, breakpoint_id: existing.id });
    } else {
      send({ type: "breakpoint:set", session_id: sessionId, node_id: nodeId });
    }
  };

  const statusColor = (status: string) => {
    const colors: Record<string, string> = {
      completed: "border-green-500 bg-green-50 dark:bg-green-950",
      running: "border-blue-500 bg-blue-50 dark:bg-blue-950 animate-pulse",
      error: "border-red-500 bg-red-50 dark:bg-red-950",
      paused: "border-yellow-500 bg-yellow-50 dark:bg-yellow-950",
      pending: "border-surface-300 bg-surface-50 dark:border-surface-600 dark:bg-surface-900",
    };
    return colors[status] || colors.pending;
  };

  return (
    <div className="flex h-screen bg-surface-50 dark:bg-surface-950">
      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b bg-white px-4 py-2 dark:border-surface-700 dark:bg-surface-900">
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-bold text-primary-600">Agent Studio</h1>
            <span className={`rounded px-2 py-0.5 text-xs ${connected ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300" : "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300"}`}>
              {connected ? "Connected" : "Disconnected"}
            </span>
            {sessionId && <span className="rounded bg-surface-100 px-2 py-0.5 text-xs text-surface-600 dark:bg-surface-700 dark:text-surface-400">Session: {sessionId.slice(0, 12)}</span>}
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => setStepMode(!stepMode)} className={`rounded-lg px-3 py-1.5 text-xs font-medium ${stepMode ? "bg-yellow-500 text-white" : "bg-surface-200 text-surface-700 dark:bg-surface-700 dark:text-surface-300"}`}>
              Step Mode {stepMode ? "ON" : "OFF"}
            </button>
            <button onClick={() => handleStep("over")} disabled={!connected} className="rounded-lg bg-surface-200 px-3 py-1.5 text-xs font-medium text-surface-700 disabled:opacity-40 dark:bg-surface-700 dark:text-surface-300">Step Over</button>
            <button onClick={() => handleStep("into")} disabled={!connected} className="rounded-lg bg-surface-200 px-3 py-1.5 text-xs font-medium text-surface-700 disabled:opacity-40 dark:bg-surface-700 dark:text-surface-300">Step Into</button>
            <button onClick={() => handleStep("out")} disabled={!connected} className="rounded-lg bg-surface-200 px-3 py-1.5 text-xs font-medium text-surface-700 disabled:opacity-40 dark:bg-surface-700 dark:text-surface-300">Step Out</button>
            <button onClick={handleRun} disabled={!connected} className={`rounded-lg px-4 py-1.5 text-xs font-medium text-white disabled:opacity-40 ${isRunning ? "bg-red-600 hover:bg-red-700" : "bg-green-600 hover:bg-green-700"}`}>
              {isRunning ? "Stop" : "Run"}
            </button>
          </div>
        </header>

        <div className="flex flex-1">
          <div className="flex-1 p-4">
            <div className="flex items-center justify-center gap-4">
              {nodes.map((node, i) => (
                <div key={node.id} className="relative">
                  <div onClick={() => toggleBreakpoint(node.id)} onContextMenu={(e) => { e.preventDefault(); toggleBreakpoint(node.id); }} className={`flex h-20 w-32 flex-col items-center justify-center rounded-xl border-2 ${statusColor(node.status)} p-2 text-center cursor-pointer hover:shadow-md transition-shadow`}>
                    <span className="text-xs font-medium text-surface-600 dark:text-surface-400">{node.type}</span>
                    <span className="text-sm font-semibold text-surface-900 dark:text-surface-50">{node.label}</span>
                    <span className="text-xs text-surface-500">{node.status}</span>
                    {breakpoints.some((b) => b.nodeId === node.id) && (
                      <span className="absolute -top-1.5 -right-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[8px] text-white">BP</span>
                    )}
                  </div>
                  {i < nodes.length - 1 && <div className="mx-auto h-2 w-0.5 bg-surface-300 dark:bg-surface-600" />}
                </div>
              ))}
            </div>
          </div>

          <div className="w-96 border-l bg-white dark:border-surface-700 dark:bg-surface-900">
            <div className="flex border-b dark:border-surface-700">
              {(["graph", "inspector", "console", "breakpoints"] as const).map((tab) => (
                <button key={tab} onClick={() => setActiveTab(tab)} className={`flex-1 px-3 py-2 text-xs font-medium ${activeTab === tab ? "border-b-2 border-primary-600 text-primary-600" : "text-surface-500 hover:text-surface-700"}`}>
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            <div className="h-[calc(100vh-120px)] overflow-y-auto p-3">
              {activeTab === "graph" && (
                <div className="space-y-2">
                  <h3 className="text-xs font-semibold text-surface-500 uppercase">Graph State</h3>
                  {nodes.map((n) => (
                    <div key={n.id} className="flex items-center justify-between rounded-lg bg-surface-50 p-2 dark:bg-surface-800">
                      <div className="flex items-center gap-2">
                        <div className={`h-2 w-2 rounded-full ${n.status === "completed" ? "bg-green-500" : n.status === "running" ? "bg-blue-500" : n.status === "error" ? "bg-red-500" : "bg-surface-300"}`} />
                        <span className="text-xs text-surface-700 dark:text-surface-300">{n.label}</span>
                      </div>
                      <span className="text-xs text-surface-400">{n.status}</span>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === "inspector" && (
                <div className="space-y-3">
                  <h3 className="text-xs font-semibold text-surface-500 uppercase">Variables</h3>
                  {Object.keys(variables).length === 0 ? (
                    <p className="text-xs text-surface-400">No variables captured yet. Run a session.</p>
                  ) : (
                    Object.entries(variables).map(([key, value]) => (
                      <div key={key} className="rounded-lg bg-surface-50 p-2 dark:bg-surface-800">
                        <p className="text-xs font-medium text-primary-600">{key}</p>
                        <pre className="mt-1 text-xs text-surface-600 dark:text-surface-400">{JSON.stringify(value, null, 2)}</pre>
                      </div>
                    ))
                  )}
                </div>
              )}

              {activeTab === "console" && (
                <div className="space-y-1">
                  <h3 className="text-xs font-semibold text-surface-500 uppercase">Logs</h3>
                  <div className="max-h-[500px] overflow-y-auto rounded-lg bg-black p-2 font-mono text-xs text-green-400">
                    {logs.map((log, i) => (
                      <p key={i} className={`${log.level === "warn" ? "text-yellow-400" : log.level === "error" ? "text-red-400" : ""}`}>
                        [{log.time}] [{log.level}] {log.message}
                      </p>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === "breakpoints" && (
                <div className="space-y-2">
                  <h3 className="text-xs font-semibold text-surface-500 uppercase">Breakpoints</h3>
                  {breakpoints.length === 0 ? (
                    <p className="text-xs text-surface-400">No breakpoints set. Right-click a node to add one.</p>
                  ) : (
                    breakpoints.map((bp) => (
                      <div key={bp.id} className="flex items-center justify-between rounded-lg bg-surface-50 p-2 dark:bg-surface-800">
                        <div className="flex items-center gap-2">
                          <div className={`h-3 w-3 rounded-full ${bp.enabled ? "bg-red-500" : "bg-surface-300"}`} />
                          <span className="text-xs text-surface-700 dark:text-surface-300">{bp.nodeId}</span>
                        </div>
                        <span className="text-xs text-surface-400">Hits: {bp.hitCount}</span>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}