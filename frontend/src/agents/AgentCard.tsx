import React from 'react';
import { Agent } from '../types/agent';
import AgentStatus from './AgentStatus';

interface AgentCardProps {
  agent: Agent;
  onStart: (id: string) => void;
  onStop: (id: string) => void;
  loading?: boolean;
}

export default function AgentCard({ agent, onStart, onStop, loading }: AgentCardProps) {
  const lastActive = agent.metrics.executions > 0
    ? new Date(agent.created_at).toLocaleDateString()
    : 'Never';

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-950 p-4 hover:border-gray-700 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 text-sm font-bold text-white">
            {agent.name.slice(0, 2).toUpperCase()}
          </div>
          <div>
            <h3 className="text-sm font-semibold text-gray-200">{agent.name}</h3>
            <AgentStatus status={agent.status} />
          </div>
        </div>
        <button
          onClick={() => agent.status === 'online' ? onStop(agent.id) : onStart(agent.id)}
          disabled={loading}
          className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
            agent.status === 'online'
              ? 'bg-red-500/10 text-red-400 hover:bg-red-500/20'
              : 'bg-green-500/10 text-green-400 hover:bg-green-500/20'
          } disabled:opacity-50`}
        >
          {loading ? '...' : agent.status === 'online' ? 'Stop' : 'Start'}
        </button>
      </div>

      <p className="mb-3 text-xs text-gray-500 line-clamp-2">
        {agent.description || 'No description provided'}
      </p>

      <div className="flex flex-wrap gap-1 mb-3">
        {agent.capabilities.map((cap) => (
          <span
            key={cap}
            className="rounded-full bg-blue-600/10 px-2 py-0.5 text-[10px] font-medium text-blue-400"
          >
            {cap}
          </span>
        ))}
      </div>

      <div className="flex items-center justify-between border-t border-gray-800 pt-2 text-[10px] text-gray-500">
        <span>Model: {agent.model}</span>
        <span>Last active: {lastActive}</span>
      </div>
    </div>
  );
}
