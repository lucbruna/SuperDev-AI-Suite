"use client";

import { useState, useRef, useEffect } from "react";

interface Message {
  id: string;
  type: "user" | "assistant" | "system" | "error";
  content: string;
  timestamp: Date;
}

const WELCOME: Message = {
  id: "welcome",
  type: "system",
  content: "AI Terminal — describe what you want to build. I'll suggest commands, fix errors, and auto-complete.",
  timestamp: new Date(),
};

export function AITerminal() {
  const [messages, setMessages] = useState<Message[]>([WELCOME]);
  const [input, setInput] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isProcessing) return;
    const userMsg: Message = {
      id: `user_${Date.now()}`,
      type: "user",
      content: input.trim(),
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsProcessing(true);

    const thinking: Message = {
      id: `think_${Date.now()}`,
      type: "system",
      content: "🤔 Thinking...",
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, thinking]);

    try {
      const res = await fetch("/api/terminal/ai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: userMsg.content }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      setMessages((prev) => prev.filter((m) => m.id !== thinking.id));
      if (data.command) {
        setMessages((prev) => [
          ...prev,
          { id: `cmd_${Date.now()}`, type: "assistant", content: `$ ${data.command}`, timestamp: new Date() },
        ]);
      }
      if (data.explanation) {
        setMessages((prev) => [
          ...prev,
          {
            id: `exp_${Date.now()}`,
            type: "assistant",
            content: data.explanation,
            timestamp: new Date(),
          },
        ]);
      }
    } catch (err: any) {
      setMessages((prev) => prev.filter((m) => m.id !== thinking.id));
      setMessages((prev) => [
        ...prev,
        {
          id: `err_${Date.now()}`,
          type: "error",
          content: err.message || "Request failed",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const copyToClipboard = (text: string) => navigator.clipboard.writeText(text);

  return (
    <div className="flex h-[500px] flex-col rounded-xl border bg-gray-950 font-mono text-sm dark:border-surface-700">
      <div className="flex items-center justify-between border-b border-gray-800 px-4 py-2">
        <span className="text-xs text-green-400">AI Terminal • v1.0</span>
        <button onClick={() => setMessages([WELCOME])} className="text-xs text-gray-500 hover:text-gray-300">Clear</button>
      </div>
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((msg) => (
          <div key={msg.id} className="mb-2 group">
            <div className="flex items-start gap-2">
              <span className="mt-0.5 shrink-0 text-xs">
                {msg.type === "user" ? ">" : msg.type === "assistant" ? "$" : msg.type === "error" ? "!" : "#"}
              </span>
              <pre className={`whitespace-pre-wrap text-xs ${msg.type === "error" ? "text-red-400" : msg.type === "system" ? "text-gray-500" : msg.type === "assistant" ? "text-green-400" : "text-gray-200"}`}>
                {msg.content}
              </pre>
              <button
                onClick={() => copyToClipboard(msg.content)}
                className="ml-auto shrink-0 opacity-0 group-hover:opacity-100 text-[10px] text-gray-600 hover:text-gray-300"
              >
                copy
              </button>
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <div className="border-t border-gray-800 p-3">
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isProcessing ? "Processing..." : "Describe your task or paste an error..."}
            disabled={isProcessing}
            className="flex-1 rounded-lg bg-gray-900 px-3 py-2 text-xs text-gray-200 placeholder-gray-600 outline-none ring-1 ring-gray-700 focus:ring-green-500"
          />
          <button
            onClick={sendMessage}
            disabled={isProcessing || !input.trim()}
            className="rounded-lg bg-green-600 px-4 py-2 text-xs font-medium text-white hover:bg-green-500 disabled:opacity-40"
          >
            {isProcessing ? "..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}