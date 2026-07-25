import React, { useMemo } from 'react';
import { Agent } from '../types/agent';
import AgentList from './AgentList';

interface AgentDashboardProps {
  agents: Agent[];
  loading: boolean;
  error: string | null;
  onStart: (id: string) => void;
  onStop: (id: string) => void;
  onStartAll: () => void;
  onStopAll: () => void;
  onRefresh: () => void;
}

export default function AgentDashboard({
  agents,
  loading,
  error,
  onStart,
  onStop,
  onStartAll,
  onStopAll,
  onRefresh,
}: AgentDashboardProps) {
  const stats = useMemo(() => {
    const total = agents.length;
    const active = agents.filter((a) => a.status === 'online' || a.status === 'busy').length;
    const failed = agents.filter((a) => a.status === 'error').length;
    const offline = agents.filter((a) => a.status === 'offline').length;
    return { total, active, failed, offline };
  }, [agents]);

  if (loading && agents.length === 0) {
    return (
      <div className="flex h-full items-center justify-center bg-gray-900">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
          <p className="text-sm text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error && agents.length === 0) {
    return (
      <div className="flex h-full items-center justify-center bg-gray-900">
        <div className="flex flex-col items-center gap-3 text-center">
          <div className="rounded-full bg-red-500/10 p-3">
            <svg className="h-6 w-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p className="text-sm text-red-400">{error}</p>
          <button onClick={onRefresh} className="rounded-md bg-blue-600 px-4 py-1.5 text-sm text-white hover:bg-blue-500">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-gray-900 p-6 overflow-y-auto">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-lg font-semibold text-gray-200">Agent Dashboard</h1>
        <div className="flex items-center gap-2">
          <button
            onClick={onStartAll}
            disabled={loading}
            className="rounded-lg bg-green-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-green-500 disabled:opacity-50"
          >
            Start All
          </button>
          <button
            onClick={onStopAll}
            disabled={loading}
            className="rounded-lg bg-red-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-500 disabled:opacity-50"
          >
            Stop All
          </button>
          <button
            onClick={onRefresh}
            disabled={loading}
            className="rounded-lg bg-gray-800 px-3 py-1.5 text-xs font-medium text-gray-300 hover:bg-gray-700 disabled:opacity-50"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="mb-6 grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="rounded-xl border border-gray-800 bg-gray-950 p-4">
          <p className="text-[10px] font-medium uppercase tracking-wider text-gray-500">Total</p>
          <p className="mt-1 text-2xl font-bold text-gray-200">{stats.total}</p>
        </div>
        <div className="rounded-xl border border-gray-800 bg-gray-950 p-4">
          <p className="text-[10px] font-medium uppercase tracking-wider text-green-400">Active</p>
          <p className="mt-1 text-2xl font-bold text-green-400">{stats.active}</p>
        </div>
        <div className="rounded-xl border border-gray-800 bg-gray-950 p-4">
          <p className="text-[10px] font-medium uppercase tracking-wider text-red-400">Failed</p>
          <p className="mt-1 text-2xl font-bold text-red-400">{stats.failed}</p>
        </div>
        <div className="rounded-xl border border-gray-800 bg-gray-950 p-4">
          <p className="text-[10px] font-medium uppercase tracking-wider text-gray-500">Offline</p>
          <p className="mt-1 text-2xl font-bold text-gray-500">{stats.offline}</p>
        </div>
      </div>

      <AgentList
        agents={agents}
        loading={loading}
        error={error}
        onStart={onStart}
        onStop={onStop}
        onRefresh={onRefresh}
      />
    </div>
  );
}
