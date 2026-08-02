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
import { refreshAccessToken } from "@/api/client";

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

const MAX_RECONNECT_ATTEMPTS = 5;
const BASE_RECONNECT_DELAY_MS = 3000;
const MAX_RECONNECT_DELAY_MS = 30000;

export function WebSocketProvider({ children, url }: WebSocketProviderProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<unknown | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const handlersRef = useRef<Map<string, Set<MessageHandler>>>(new Map());
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout>>();
  const reconnectAttemptsRef = useRef(0);
  const accessToken = useAuthStore((s) => s.accessToken);
  const wsUrl = url ?? process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws";

  // Always points at the latest `connect` so scheduled retries never use a
  // stale closure (avoids a circular dependency between the two callbacks).
  const connectRef = useRef<() => void>(() => {});

  const connect = useCallback(() => {
    const scheduleRetry = () => {
      if (reconnectAttemptsRef.current >= MAX_RECONNECT_ATTEMPTS) return;
      reconnectAttemptsRef.current++;
      const delay = Math.min(
        BASE_RECONNECT_DELAY_MS * Math.pow(2, reconnectAttemptsRef.current - 1),
        MAX_RECONNECT_DELAY_MS,
      );
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = setTimeout(() => connectRef.current(), delay);
    };

    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    // Read the token from the store at call time (not from a closure): after
    // a successful refresh the scheduled reconnect must use the NEW token,
    // otherwise it would keep reconnecting with the expired one forever.
    const token = useAuthStore.getState().accessToken;
    if (!token) return;

    try {
      const ws = new WebSocket(`${wsUrl}?token=${token}`);

      ws.onopen = () => {
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;
      };

      ws.onclose = async (event) => {
        setIsConnected(false);
        wsRef.current = null;

        // Auth failure (4003) or policy violation (4001) — try refreshing the
        // token first, then reconnect once with the fresh session.
        const isAuthError = event.code === 4001 || event.code === 4003;

        if (isAuthError && reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
          const refreshed = await refreshAccessToken();
          if (refreshed) {
            reconnectAttemptsRef.current++;
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = setTimeout(() => connectRef.current(), 1000);
            return;
          }
          // Refresh token also expired — end the session.
          useAuthStore.getState().logout();
          return;
        }

        // Non-auth error — reconnect with exponential backoff.
        scheduleRetry();
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
      scheduleRetry();
    }
  }, [wsUrl]);

  // Keep the ref in sync with the latest `connect`.
  useEffect(() => {
    connectRef.current = connect;
  }, [connect]);

  // Connect once a session exists (e.g. right after login) and stop
  // reconnecting when the user logs out.
  useEffect(() => {
    if (!accessToken) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectAttemptsRef.current = 0;
      wsRef.current?.close();
      return;
    }
    // Cancel any pending scheduled reconnect — this effect-driven connect
    // supersedes it, otherwise both could fire while the first socket is
    // still CONNECTING and create a duplicate connection.
    clearTimeout(reconnectTimeoutRef.current);
    const state = wsRef.current?.readyState;
    if (state !== WebSocket.OPEN && state !== WebSocket.CONNECTING) {
      connect();
    }
  }, [accessToken, connect]);

  // Cleanup on unmount only — never on token changes (that would drop the
  // live socket on every refresh).
  useEffect(() => {
    return () => {
      clearTimeout(reconnectTimeoutRef.current);
      wsRef.current?.close();
    };
  }, []);

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
