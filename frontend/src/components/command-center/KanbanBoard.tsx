"use client";

import { useState, useEffect } from "react";
import { getAgents } from "@/api/agents";

const COLUMNS = [
  { id: "planning", title: "Planning", color: "bg-yellow-500" },
  { id: "executing", title: "Executing", color: "bg-blue-500" },
  { id: "review", title: "Review", color: "bg-purple-500" },
  { id: "done", title: "Done", color: "bg-green-500" },
];

interface AgentCardData {
  id: string;
  name: string;
  role: string;
  status: string;
  progress: number;
  task: string;
  started_at: string;
}

function mapStatus(agentStatus: string): string {
  switch (agentStatus) {
    case "running": return "executing";
    case "error": return "review";
    case "completed":
    case "stopped": return "done";
    default: return "planning";
  }
}

export function KanbanBoard() {
  const [agents, setAgents] = useState<AgentCardData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAgents().then((data) => {
      const mapped: AgentCardData[] = (Array.isArray(data) ? data : []).map((a: any) => ({
        id: a.id,
        name: a.name,
        role: a.agent_type || "Agent",
        status: mapStatus(a.status),
        progress: a.status === "running" ? 50 + Math.floor(Math.random() * 40) : a.status === "idle" ? 0 : 100,
        task: a.description || "No task assigned",
        started_at: "—",
      }));
      setAgents(mapped);
      setLoading(false);
    }).catch(() => {
      setLoading(false);
    });
  }, []);

  const getColumnCards = (columnId: string) => agents.filter((a) => a.status === columnId);

  return (
    <div className="grid grid-cols-4 gap-3">
      {COLUMNS.map((col) => {
        const cards = getColumnCards(col.id);
        return (
          <div key={col.id} className="rounded-xl border dark:border-surface-700">
            <div className={`flex items-center justify-between rounded-t-xl ${col.color} px-3 py-2`}>
              <span className="text-xs font-semibold text-white">{col.title}</span>
              <span className="rounded-full bg-white/30 px-2 py-0.5 text-[10px] text-white">{cards.length}</span>
            </div>
            <div className="min-h-[300px] space-y-2 bg-surface-50 p-2 dark:bg-surface-900">
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
                </div>
              ) : cards.length === 0 ? (
                <p className="py-4 text-center text-[10px] text-surface-400">No agents</p>
              ) : (
                cards.map((agent) => (
                  <div key={agent.id} className="rounded-lg border bg-white p-3 shadow-sm dark:border-surface-700 dark:bg-surface-800">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-surface-900 dark:text-surface-50">{agent.name}</span>
                      <span className="rounded-full bg-surface-200 px-1.5 py-0.5 text-[9px] text-surface-600 dark:bg-surface-700 dark:text-surface-300">{agent.role}</span>
                    </div>
                    <p className="mt-1 text-[10px] text-surface-500">{agent.task}</p>
                    <div className="mt-2">
                      <div className="flex items-center justify-between text-[9px] text-surface-400">
                        <span>{agent.progress}%</span>
                        <span>{agent.started_at}</span>
                      </div>
                      <div className="mt-1 h-1 w-full overflow-hidden rounded-full bg-surface-200 dark:bg-surface-700">
                        <div className={`h-full rounded-full transition-all ${col.color} opacity-70`} style={{ width: `${agent.progress}%` }} />
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
