import React, { useState, useRef, useEffect, useCallback } from 'react';

interface LogEntry {
  id: string;
  level: 'info' | 'warn' | 'error';
  message: string;
  timestamp: number;
  source?: string;
}

const LOG_COLORS: Record<string, string> = {
  info: 'text-blue-400',
  warn: 'text-yellow-400',
  error: 'text-red-400',
};

const LOG_BG: Record<string, string> = {
  info: 'bg-blue-500/5',
  warn: 'bg-yellow-500/5',
  error: 'bg-red-500/10',
};

interface AgentConsoleProps {
  logs: LogEntry[];
  isStreaming?: boolean;
  onClear: () => void;
  onLevelFilter: (level: string) => void;
  levelFilter: string;
}

export default function AgentConsole({
  logs,
  isStreaming,
  onClear,
  onLevelFilter,
  levelFilter,
}: AgentConsoleProps) {
  const [autoScroll, setAutoScroll] = useState(true);
  const [search, setSearch] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  const filtered = logs.filter((entry) => {
    if (levelFilter !== 'all' && entry.level !== levelFilter) return false;
    if (search && !entry.message.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [filtered.length, autoScroll]);

  const formatTime = (ts: number) => {
    const d = new Date(ts);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  return (
    <div className="flex h-full flex-col bg-gray-950 rounded-xl border border-gray-800">
      <div className="flex items-center justify-between border-b border-gray-800 px-4 py-2">
        <div className="flex items-center gap-3">
          <h3 className="text-sm font-semibold text-gray-300">Agent Console</h3>
          {isStreaming && (
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 animate-pulse rounded-full bg-green-500" />
              <span className="text-[10px] text-green-400">Live</span>
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <div className="flex rounded-md border border-gray-700 overflow-hidden">
            {['all', 'info', 'warn', 'error'].map((level) => (
              <button
                key={level}
                onClick={() => onLevelFilter(level)}
                className={`px-2.5 py-1 text-[10px] font-medium transition-colors ${
                  levelFilter === level
                    ? 'bg-gray-800 text-gray-200'
                    : 'text-gray-500 hover:bg-gray-800 hover:text-gray-400'
                }`}
              >
                {level.toUpperCase()}
              </button>
            ))}
          </div>
          <button
            onClick={() => setAutoScroll(!autoScroll)}
            className={`rounded p-1.5 ${autoScroll ? 'text-blue-400' : 'text-gray-500 hover:text-gray-300'}`}
            title="Auto-scroll"
          >
            <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
          </button>
          <button
            onClick={onClear}
            className="rounded p-1.5 text-gray-500 hover:text-gray-300"
            title="Clear logs"
          >
            <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>

      <div className="border-b border-gray-800 px-4 py-2">
        <div className="relative">
          <svg
            className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-gray-500"
            fill="none" viewBox="0 0 24 24" stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search logs..."
            className="w-full rounded-md border border-gray-700 bg-gray-900 py-1.5 pl-9 pr-3 text-xs text-gray-300 placeholder-gray-500 focus:border-blue-500 focus:outline-none"
          />
        </div>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-2 font-mono text-[11px] leading-relaxed">
        {filtered.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-600">No log entries</p>
          </div>
        )}
        {filtered.map((entry) => (
          <div
            key={entry.id}
            className={`flex gap-2 rounded px-2 py-0.5 ${LOG_BG[entry.level]} hover:bg-gray-800/50`}
          >
            <span className="shrink-0 text-gray-600">{formatTime(entry.timestamp)}</span>
            <span className={`shrink-0 font-semibold ${LOG_COLORS[entry.level]}`}>
              [{entry.level.toUpperCase()}]
            </span>
            {entry.source && (
              <span className="shrink-0 text-gray-500">{entry.source}:</span>
            )}
            <span className="text-gray-300">{entry.message}</span>
          </div>
        ))}
      </div>

      <div className="border-t border-gray-800 px-4 py-1.5 text-[10px] text-gray-600">
        {filtered.length} entries
      </div>
    </div>
  );
}
