"use client";

import React, { useRef, useEffect, useState } from "react";
import { useTerminalStore } from "@/stores/terminalStore";
import { Button } from "@/components/buttons/Button";

interface TerminalProps {
  className?: string;
}

export function Terminal({ className = "" }: TerminalProps) {
  const termRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [input, setInput] = useState("");
  const [isReady, setIsReady] = useState(false);
  const { sessions, activeSessionId, appendOutput, createSession } = useTerminalStore();

  useEffect(() => {
    if (sessions.length === 0) {
      createSession();
    }
    setIsReady(true);
  }, []);

  const activeSessionData = sessions.find((s) => s.id === activeSessionId);
  const outputLines = activeSessionData?.output || [];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    appendOutput(activeSessionId || "", `> ${input}`);
    setInput("");

    try {
      const response = await fetch("/api/v1/runtime/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          language: "shell",
          code: input,
          max_execution_time_seconds: 30,
        }),
      });
      const data = await response.json();
      if (data.stdout) appendOutput(activeSessionId || "", data.stdout);
      if (data.stderr) appendOutput(activeSessionId || "", data.stderr);
    } catch (err) {
      appendOutput(activeSessionId || "", `Error: ${err}`);
    }
  };

  useEffect(() => {
    if (termRef.current) {
      termRef.current.scrollTop = termRef.current.scrollHeight;
    }
  }, [outputLines]);

  return (
    <div className={`flex flex-col h-full bg-[#1e1e1e] rounded-lg overflow-hidden ${className}`}>
      <div className="flex items-center justify-between px-3 py-1.5 bg-[#2d2d2d] border-b border-[#404040]">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-[#ff5f56]" />
            <div className="w-3 h-3 rounded-full bg-[#ffbd2e]" />
            <div className="w-3 h-3 rounded-full bg-[#27c93f]" />
          </div>
          <span className="text-xs text-[#808080] ml-2">Terminal</span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => createSession()}
          className="text-xs text-[#808080] hover:text-white"
        >
          + New
        </Button>
      </div>

      <div
        ref={termRef}
        className="flex-1 overflow-y-auto p-3 font-mono text-sm text-[#d4d4d4]"
        onClick={() => inputRef.current?.focus()}
      >
        {outputLines.map((line, i) => (
          <div key={i} className="whitespace-pre-wrap leading-5">
            {line}
          </div>
        ))}

        <form onSubmit={handleSubmit} className="flex items-center gap-2 mt-1">
          <span className="text-[#4ec9b0]">$</span>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 bg-transparent outline-none text-[#d4d4d4] font-mono text-sm"
            placeholder="Type a command..."
            autoFocus
          />
        </form>
      </div>
    </div>
  );
}
