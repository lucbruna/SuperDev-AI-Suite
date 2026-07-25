"use client";

import { useEffect, useRef, useState } from "react";

interface LogStreamProps {
  url: string;
}

export function LogStream({ url }: LogStreamProps) {
  const [logs, setLogs] = useState<string[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(url);
    wsRef.current = ws;
    ws.onopen = () => setConnected(true);
    ws.onmessage = (event) => {
      setLogs((prev) => [...prev.slice(-100), event.data]);
    };
    ws.onclose = () => setConnected(false);
    return () => ws.close();
  }, [url]);

  return (
    <div className="bg-black text-green-400 font-mono text-sm p-4 rounded-lg h-64 overflow-y-auto">
      <div className="flex items-center gap-2 mb-2">
        <span
          className={`h-2 w-2 rounded-full ${connected ? "bg-green-400" : "bg-red-400"}`}
        />
        <span className="text-xs">{connected ? "Connected" : "Disconnected"}</span>
      </div>
      {logs.map((line, i) => (
        <div key={i} className="whitespace-pre-wrap leading-5">
          {line}
        </div>
      ))}
    </div>
  );
}