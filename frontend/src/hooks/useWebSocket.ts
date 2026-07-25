"use client";

import { useContext, useEffect } from "react";
import { WebSocketContext } from "@/providers/WebSocketProvider";

export function useWebSocket() {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error("useWebSocket must be used within a WebSocketProvider");
  }
  return context;
}

export function useWebSocketEvent<T = unknown>(
  event: string,
  handler: (data: T) => void,
) {
  const { subscribe } = useWebSocket();

  useEffect(() => {
    const unsubscribe = subscribe(event, handler as (data: unknown) => void);
    return unsubscribe;
  }, [event, handler, subscribe]);
}
