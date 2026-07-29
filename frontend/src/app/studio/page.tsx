"use client";

import { useEffect, useRef, useState } from "react";
import { DashboardLayout } from "@/components/DashboardLayout";
import { ENV } from "@/config/environment";

export default function StudioPage() {
  const wsRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [nodes, setNodes] = useState<any[]>([]);

  useEffect(() => {
    const ws = new WebSocket(`${ENV.WS_URL}/studio/ws`);
    ws.onopen = () => setConnected(true);
    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.type === "nodes") setNodes(data.nodes || []);
      } catch {}
    };
    ws.onclose = () => setConnected(false);
    wsRef.current = ws;
    return () => ws.close();
  }, []);

  return (
    <DashboardLayout>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">Studio</h1>
        <span className={`rounded-full px-3 py-1 text-xs font-medium ${connected ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
          {connected ? "Conectado" : "Desconectado"}
        </span>
      </div>
      <div className="rounded-xl border bg-white p-6 dark:border-surface-700 dark:bg-surface-900">
        {nodes.length === 0 ? (
          <p className="text-surface-400 text-center py-12">Conecte-se ao WebSocket para ver os nós do studio.</p>
        ) : (
          <div className="space-y-2">
            {nodes.map((node: any, i: number) => (
              <div key={i} className="rounded-lg bg-surface-50 p-3 text-sm dark:bg-surface-800">
                {node.name || node.id || `Node ${i + 1}`}
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
