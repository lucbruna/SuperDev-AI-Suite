"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { ENV } from "@/config/environment";

export function CollaborativeEditor() {
  const [sessionId, setSessionId] = useState("");
  const [connected, setConnected] = useState(false);
  const [users, setUsers] = useState(1);
  const [content, setContent] = useState("");
  const [cursorPos, setCursorPos] = useState(0);
  const [remoteCursors, setRemoteCursors] = useState<Record<string, number>>({});
  const wsRef = useRef<WebSocket | null>(null);
  const userIdRef = useRef(`user_${Math.random().toString(36).slice(2, 8)}`);

  const connect = useCallback(() => {
    if (!sessionId.trim()) return;
    const ws = new WebSocket(`${ENV.WS_URL}/api/collab/ws/${encodeURIComponent(sessionId)}?user_id=${userIdRef.current}`);
    ws.onopen = () => setConnected(true);
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "init") {
          setContent(msg.content);
          setUsers(msg.users);
        } else if (msg.type === "op") {
          setContent((prev) => {
            const op = msg.op;
            if (op.kind === "insert") return prev.slice(0, op.position) + op.text + prev.slice(op.position);
            if (op.kind === "delete") return prev.slice(0, op.position) + prev.slice(op.position + (op.length || 0));
            if (op.kind === "replace") return prev.slice(0, op.position) + op.text + prev.slice(op.position + (op.length || 0));
            return prev;
          });
        } else if (msg.type === "cursor") {
          setRemoteCursors((prev) => ({ ...prev, [msg.user_id]: msg.position }));
        }
      } catch {}
    };
    ws.onclose = () => { setConnected(false); };
    wsRef.current = ws;
  }, [sessionId]);

  const sendOp = (kind: string, position: number, text?: string, length?: number) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    wsRef.current.send(JSON.stringify({ type: "op", op: { kind, position, text, length } }));
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = e.target.value;
    const oldLen = content.length;
    const newLen = newContent.length;
    const diff = newLen - oldLen;
    if (diff > 0) {
      sendOp("insert", cursorPos, newContent.slice(cursorPos, cursorPos + diff));
    } else if (diff < 0) {
      sendOp("delete", cursorPos + diff, undefined, -diff);
    }
    setContent(newContent);
  };

  const handleCursor = (e: React.MouseEvent | React.KeyboardEvent) => {
    const target = e.target as HTMLTextAreaElement;
    setCursorPos(target.selectionStart);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "cursor", position: target.selectionStart }));
    }
  };

  const disconnect = () => {
    wsRef.current?.close();
    setConnected(false);
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <input value={sessionId} onChange={(e) => setSessionId(e.target.value)} placeholder="Session name..." className="flex-1 rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800" />
        {!connected ? (
          <button onClick={connect} disabled={!sessionId.trim()} className="rounded-lg bg-primary-600 px-4 py-2 text-xs font-medium text-white hover:bg-primary-700 disabled:opacity-40">Join</button>
        ) : (
          <button onClick={disconnect} className="rounded-lg bg-red-600 px-4 py-2 text-xs font-medium text-white hover:bg-red-700">Leave</button>
        )}
      </div>

      {connected && (
        <>
          <div className="flex items-center gap-2 text-[10px] text-surface-500">
            <span className={`h-2 w-2 rounded-full ${connected ? "bg-green-500" : "bg-red-500"}`} />
            {connected ? `Connected · ${users} user${users !== 1 ? "s" : ""}` : "Disconnected"}
            {Object.keys(remoteCursors).length > 0 && <span>· {Object.keys(remoteCursors).length} remote cursor(s)</span>}
          </div>

          <div className="relative">
            <textarea value={content} onChange={handleChange} onClick={handleCursor} onKeyUp={handleCursor} className="h-[400px] w-full rounded-xl border bg-white p-4 font-mono text-xs leading-relaxed dark:border-surface-700 dark:bg-surface-900 dark:text-surface-100" placeholder="Start typing together..." />
            {Object.entries(remoteCursors).map(([uid, pos]) => {
              const line = content.slice(0, pos).split("\n").length;
              return <div key={uid} className="pointer-events-none absolute left-0 top-0 text-[9px] text-blue-500" style={{ top: `${line * 18}px` }}>▎{uid.slice(0, 5)}</div>;
            })}
          </div>
        </>
      )}
    </div>
  );
}