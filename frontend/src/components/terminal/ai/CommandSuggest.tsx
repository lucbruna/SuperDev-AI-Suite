"use client";

import { useState, useEffect } from "react";

interface Suggestion {
  command: string;
  description: string;
  category: string;
}

const DEFAULT_SUGGESTIONS: Suggestion[] = [
  { command: "superdev agent create --name", description: "Create a new agent", category: "agents" },
  { command: "superdev plan generate", description: "Generate project plan", category: "planning" },
  { command: "superdev code review", description: "Review current codebase", category: "code" },
  { command: "superdev deploy --env staging", description: "Deploy to staging", category: "devops" },
  { command: "superdev test run", description: "Run test suite", category: "testing" },
  { command: "superdev docs generate", description: "Generate documentation", category: "docs" },
  { command: "superdev workflow execute", description: "Execute a workflow", category: "workflow" },
  { command: "superdev cost report --period week", description: "Weekly cost report", category: "cost" },
  { command: "superdev backup create", description: "Create a backup", category: "backup" },
  { command: "superdev audit trail --days 7", description: "Last 7 days audit", category: "audit" },
];

interface CommandSuggestProps {
  onSelect: (command: string) => void;
  search: string;
}

export function CommandSuggest({ onSelect, search }: CommandSuggestProps) {
  const [suggestions, setSuggestions] = useState<Suggestion[]>(DEFAULT_SUGGESTIONS);

  useEffect(() => {
    if (!search.trim()) {
      setSuggestions(DEFAULT_SUGGESTIONS.slice(0, 5));
      return;
    }
    const lower = search.toLowerCase();
    setSuggestions(
      DEFAULT_SUGGESTIONS.filter((s) => s.command.toLowerCase().includes(lower) || s.description.toLowerCase().includes(lower))
    );
  }, [search]);

  return (
    <div className="absolute bottom-full left-0 right-0 mb-1 rounded-lg border border-surface-700 bg-surface-800 shadow-xl">
      {suggestions.map((s) => (
        <button
          key={s.command}
          onClick={() => onSelect(s.command)}
          className="flex w-full items-center gap-3 px-3 py-2 text-left hover:bg-surface-700"
        >
          <span className="text-[10px] font-medium uppercase text-primary-400 shrink-0 w-12">{s.category}</span>
          <span className="text-xs text-gray-200 font-mono">{s.command}</span>
          <span className="ml-auto text-xs text-gray-500">{s.description}</span>
        </button>
      ))}
      {suggestions.length === 0 && (
        <p className="px-3 py-2 text-xs text-gray-500">No suggestions found</p>
      )}
    </div>
  );
}