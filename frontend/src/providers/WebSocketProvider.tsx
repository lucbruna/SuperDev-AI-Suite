"use client";

import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { useAuthStore } from "@/stores/authStore";

type MessageHandler = (data: unknown) => void;

interface WebSocketContextValue {
  isConnected: boolean;
  lastMessage: unknown | null;
  send: (message: string | Record<string, unknown>) => void;
  subscribe: (event: string, handler: MessageHandler) => () => void;
  reconnect: () => void;
}

export const WebSocketContext = createContext<WebSocketContextValue | null>(null);

interface WebSocketProviderProps {
  children: ReactNode;
  url?: string;
}

export function WebSocketProvider({ children, url }: WebSocketProviderProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<unknown | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const handlersRef = useRef<Map<string, Set<MessageHandler>>>(new Map());
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout>>();
  const accessToken = useAuthStore((s) => s.accessToken);
  const wsUrl = url ?? process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws";

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    if (!accessToken) return;

    try {
      const ws = new WebSocket(`${wsUrl}?token=${accessToken}`);

      ws.onopen = () => setIsConnected(true);

      ws.onclose = () => {
        setIsConnected(false);
        reconnectTimeoutRef.current = setTimeout(connect, 3000);
      };

      ws.onerror = () => {
        ws.close();
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);

          const { event: eventType, payload } = data;
          const handlers = handlersRef.current.get(eventType);
          if (handlers) {
            handlers.forEach((handler) => handler(payload));
          }

          const wildcardHandlers = handlersRef.current.get("*");
          if (wildcardHandlers) {
            wildcardHandlers.forEach((handler) => handler(data));
          }
        } catch {
          setLastMessage(event.data);
        }
      };

      wsRef.current = ws;
    } catch {
      reconnectTimeoutRef.current = setTimeout(connect, 3000);
    }
  }, [accessToken, wsUrl]);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectTimeoutRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const send = useCallback((message: string | Record<string, unknown>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(typeof message === "string" ? message : JSON.stringify(message));
    }
  }, []);

  const subscribe = useCallback((event: string, handler: MessageHandler) => {
    if (!handlersRef.current.has(event)) {
      handlersRef.current.set(event, new Set());
    }
    handlersRef.current.get(event)!.add(handler);

    return () => {
      handlersRef.current.get(event)?.delete(handler);
    };
  }, []);

  const reconnect = useCallback(() => {
    wsRef.current?.close();
    clearTimeout(reconnectTimeoutRef.current);
    connect();
  }, [connect]);

  const value = useMemo(
    () => ({ isConnected, lastMessage, send, subscribe, reconnect }),
    [isConnected, lastMessage, send, subscribe, reconnect],
  );

  return <WebSocketContext.Provider value={value}>{children}</WebSocketContext.Provider>;
}
