"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { DashboardLayout } from "@/components/DashboardLayout";
import { ENV } from "@/config/environment";

/**
 * Studio page — visual workflow/node editor.
 * Connects to backend WebSocket at /studio/ws.
 * Gracefully handles missing backend WS endpoint.
 */
export default function StudioPage() {
  const wsRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nodes, setNodes] = useState<any[]>([]);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(`${ENV.WS_URL}/studio/ws`);

      ws.onopen = () => {
        setConnected(true);
        setError(null);
      };

      ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          if (data.type === "nodes") setNodes(data.nodes || []);
        } catch {
          // ignore malformed messages
        }
      };

      ws.onerror = () => {
        setConnected(false);
        setError("WebSocket connection failed — Studio requires backend WebSocket support.");
      };

      ws.onclose = () => {
        setConnected(false);
        // Don't auto-reconnect if we already know it fails
        if (!error) {
          reconnectTimer.current = setTimeout(() => {
            if (!wsRef.current || wsRef.current.readyState === WebSocket.CLOSED) {
              connect();
            }
          }, 10000);
        }
      };

      wsRef.current = ws;
    } catch {
      setError("Could not connect to Studio WebSocket.");
    }
  }, [error]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <DashboardLayout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">Studio</h1>
          <p className="mt-1 text-sm text-surface-500">Editor visual de workflows e nós</p>
        </div>
        <div className="flex items-center gap-3">
          <span
            className={`flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium ${
              connected
                ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                : "bg-surface-100 text-surface-500 dark:bg-surface-800 dark:text-surface-400"
            }`}
          >
            <span className={`h-2 w-2 rounded-full ${connected ? "bg-green-500" : "bg-surface-400"}`} />
            {connected ? "Conectado" : "Desconectado"}
          </span>
        </div>
      </div>

      {error ? (
        <div className="rounded-xl border bg-white p-12 text-center shadow-sm dark:border-surface-700 dark:bg-surface-900">
          <div className="mb-4 text-5xl">🎨</div>
          <h2 className="mb-2 text-xl font-semibold text-surface-700 dark:text-surface-200">
            Studio
          </h2>
          <p className="mb-4 text-sm text-surface-500 max-w-md mx-auto">
            O Studio permite criar e editar workflows visualmente com um canvas de nós interativo.
          </p>
          <div className="rounded-lg bg-surface-50 p-4 text-sm text-surface-500 dark:bg-surface-800">
            {error}
          </div>
          <p className="mt-4 text-xs text-surface-400">
            Para usar o Studio, inicie o servidor backend com suporte a WebSocket em {ENV.WS_URL}
          </p>
        </div>
      ) : !connected ? (
        <div className="rounded-xl border bg-white p-12 text-center shadow-sm dark:border-surface-700 dark:bg-surface-900">
          <div className="mb-4 text-5xl">🎨</div>
          <h2 className="mb-2 text-xl font-semibold text-surface-700 dark:text-surface-200">
            Conectando ao Studio...
          </h2>
          <p className="text-sm text-surface-500">
            Aguardando conexão WebSocket com o backend.
          </p>
        </div>
      ) : nodes.length === 0 ? (
        <div className="rounded-xl border bg-white p-12 text-center shadow-sm dark:border-surface-700 dark:bg-surface-900">
          <div className="mb-4 text-5xl">🎨</div>
          <h2 className="mb-2 text-xl font-semibold text-surface-700 dark:text-surface-200">
            Studio Conectado
          </h2>
          <p className="text-sm text-surface-500">
            Nenhum nó carregado. Use o backend para enviar nós do studio.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {nodes.map((node: any, i: number) => (
            <div
              key={i}
              className="rounded-lg border bg-white p-4 text-sm shadow-sm dark:border-surface-700 dark:bg-surface-900"
            >
              <div className="flex items-center gap-3">
                <span className="text-lg">📦</span>
                <div>
                  <p className="font-medium text-surface-900 dark:text-surface-50">
                    {node.name || node.id || `Node ${i + 1}`}
                  </p>
                  {node.type && (
                    <p className="text-xs text-surface-500">{node.type}</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
}
