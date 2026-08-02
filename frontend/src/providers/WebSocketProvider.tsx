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
import { API_BASE_URL } from "@/constants/api";

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
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  const accessToken = useAuthStore((s) => s.accessToken);
  const refreshToken = useAuthStore((s) => s.refreshToken);
  const setTokens = useAuthStore((s) => s.setTokens);
  const wsUrl = url ?? process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws";

  const refreshAccessToken = useCallback(async () => {
    if (!refreshToken) return false;
    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      if (!response.ok) return false;
      const data = await response.json();
      const access_token = data.access_token || data.accessToken;
      const new_refresh_token = data.refresh_token || data.refreshToken;
      if (access_token && new_refresh_token) {
        setTokens(access_token, new_refresh_token);
        return true;
      }
    } catch {
      // refresh failed
    }
    return false;
  }, [refreshToken, setTokens]);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    if (!accessToken) return;

    try {
      const ws = new WebSocket(`${wsUrl}?token=${accessToken}`);

      ws.onopen = () => {
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;
      };

      ws.onclose = async (event) => {
        setIsConnected(false);
        wsRef.current = null;

        // Auth failure (4003) or policy violation (4001) — try refreshing token first
        const isAuthError = event.code === 4001 || event.code === 4003;

        if (isAuthError && reconnectAttemptsRef.current < maxReconnectAttempts) {
          const refreshed = await refreshAccessToken();
          if (refreshed) {
            reconnectAttemptsRef.current++;
            reconnectTimeoutRef.current = setTimeout(connect, 1000);
            return;
          }
          // Refresh token also expired - logout user
          useAuthStore.getState().logout();
          return;
        }

        // Non-auth error or auth refresh failed — reconnect with backoff
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          const delay = Math.min(3000 * Math.pow(2, reconnectAttemptsRef.current - 1), 30000);
          reconnectTimeoutRef.current = setTimeout(connect, delay);
        }
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
      if (reconnectAttemptsRef.current < maxReconnectAttempts) {
        reconnectAttemptsRef.current++;
        const delay = Math.min(3000 * Math.pow(2, reconnectAttemptsRef.current - 1), 30000);
        reconnectTimeoutRef.current = setTimeout(connect, delay);
      }
    }
  }, [wsUrl, refreshAccessToken]);

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
    reconnectAttemptsRef.current = 0;
    connect();
  }, [connect]);

  const value = useMemo(
    () => ({ isConnected, lastMessage, send, subscribe, reconnect }),
    [isConnected, lastMessage, send, subscribe, reconnect],
  );

  return <WebSocketContext.Provider value={value}>{children}</WebSocketContext.Provider>;
}
