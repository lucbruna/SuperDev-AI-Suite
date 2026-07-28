"use client";

import { useState } from "react";

interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
}

const INITIAL_MESSAGES: ChatMessage[] = [
  { id: "m1", role: "system", content: "Session started — context from previous session restored", timestamp: "10:30:00" },
  { id: "m2", role: "user", content: "What was the last task we worked on?", timestamp: "10:30:05" },
  { id: "m3", role: "assistant", content: "We were implementing the MCP Protocol support. You created the server, client, registry, and frontend components. The last file was MCPBrowser.tsx.", timestamp: "10:30:07" },
  { id: "m4", role: "user", content: "Can you continue with the debugger integration?", timestamp: "10:30:15" },
  { id: "m5", role: "assistant", content: "Yes! The Agent Studio already has the backend (studio.py, breakpoint.py, inspector.py) at 80%. I'll connect the WebSocket real-time now.", timestamp: "10:30:18" },
];

export function ChatHistory() {
  const [messages] = useState<ChatMessage[]>(INITIAL_MESSAGES);
  const [searchQuery, setSearchQuery] = useState("");

  const filtered = searchQuery.trim()
    ? messages.filter((m) => m.content.toLowerCase().includes(searchQuery.toLowerCase()))
    : messages;

  const groupedByDate = groupBy(filtered, (m) => {
    const d = new Date();
    return d.toLocaleDateString();
  });

  return (
    <div className="rounded-xl border dark:border-surface-700">
      <div className="border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">Chat History ({messages.length} messages)</span>
          <input value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} placeholder="Search history..." className="w-36 rounded border border-surface-300 bg-white px-2 py-1 text-[10px] dark:border-surface-600 dark:bg-surface-800" />
        </div>
      </div>
      <div className="max-h-[400px] space-y-3 overflow-y-auto p-3">
        {Array.from(groupedByDate.entries()).map(([date, msgs]) => (
          <div key={date}>
            <p className="mb-1 text-[9px] font-medium text-surface-400">{date}</p>
            <div className="space-y-2">
              {msgs.map((m) => (
                <div key={m.id} className="flex items-start gap-2">
                  <span className={`mt-0.5 shrink-0 rounded px-1 py-0.5 text-[8px] font-medium ${m.role === "user" ? "bg-primary-100 text-primary-700" : m.role === "assistant" ? "bg-green-100 text-green-700" : "bg-surface-200 text-surface-600"}`}>
                    {m.role}
                  </span>
                  <div>
                    <p className="text-xs text-surface-700 dark:text-surface-300">{m.content}</p>
                    <p className="text-[9px] text-surface-400">{m.timestamp}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function groupBy<T>(arr: T[], fn: (item: T) => string): Map<string, T[]> {
  const map = new Map<string, T[]>();
  for (const item of arr) {
    const key = fn(item);
    if (!map.has(key)) map.set(key, []);
    map.get(key)!.push(item);
  }
  return map;
}