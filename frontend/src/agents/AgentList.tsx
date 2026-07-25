import React, { useState, useMemo } from 'react';
import { Agent, AgentStatus as AgentStatusType } from '../types/agent';
import AgentCard from './AgentCard';

interface AgentListProps {
  agents: Agent[];
  loading: boolean;
  error: string | null;
  onStart: (id: string) => void;
  onStop: (id: string) => void;
  onRefresh: () => void;
}

export default function AgentList({
  agents,
  loading,
  error,
  onStart,
  onStop,
  onRefresh,
}: AgentListProps) {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<AgentStatusType | 'all'>('all');
  const [capabilityFilter, setCapabilityFilter] = useState<string>('all');
  const [layout, setLayout] = useState<'grid' | 'list'>('grid');

  const allCapabilities = useMemo(() => {
    const set = new Set<string>();
    agents.forEach((a) => a.capabilities.forEach((c) => set.add(c)));
    return Array.from(set);
  }, [agents]);

  const filtered = useMemo(() => {
    return agents.filter((a) => {
      if (search && !a.name.toLowerCase().includes(search.toLowerCase()) && !a.description.toLowerCase().includes(search.toLowerCase())) return false;
      if (statusFilter !== 'all' && a.status !== statusFilter) return false;
      if (capabilityFilter !== 'all' && !a.capabilities.includes(capabilityFilter)) return false;
      return true;
    });
  }, [agents, search, statusFilter, capabilityFilter]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
          <p className="text-sm text-gray-400">Loading agents...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-20">
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
    <div>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <svg className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search agents..."
            className="w-full rounded-lg border border-gray-700 bg-gray-900 py-2 pl-10 pr-3 text-sm text-gray-300 placeholder-gray-500 focus:border-blue-500 focus:outline-none"
          />
        </div>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as AgentStatusType | 'all')}
          className="rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-xs text-gray-300 focus:border-blue-500 focus:outline-none"
        >
          <option value="all">All Status</option>
          <option value="online">Online</option>
          <option value="offline">Offline</option>
          <option value="busy">Busy</option>
          <option value="error">Error</option>
        </select>

        <select
          value={capabilityFilter}
          onChange={(e) => setCapabilityFilter(e.target.value)}
          className="rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-xs text-gray-300 focus:border-blue-500 focus:outline-none"
        >
          <option value="all">All Capabilities</option>
          {allCapabilities.map((cap) => (
            <option key={cap} value={cap}>{cap}</option>
          ))}
        </select>

        <div className="flex rounded-lg border border-gray-700 overflow-hidden">
          <button
            onClick={() => setLayout('grid')}
            className={`p-2 ${layout === 'grid' ? 'bg-gray-800 text-gray-200' : 'bg-gray-900 text-gray-500 hover:bg-gray-800'}`}
            title="Grid view"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
          </button>
          <button
            onClick={() => setLayout('list')}
            className={`p-2 ${layout === 'list' ? 'bg-gray-800 text-gray-200' : 'bg-gray-900 text-gray-500 hover:bg-gray-800'}`}
            title="List view"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>

      {filtered.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="rounded-full bg-gray-800 p-4 mb-3">
            <svg className="h-8 w-8 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <p className="text-sm text-gray-500">No agents found</p>
          {search || statusFilter !== 'all' || capabilityFilter !== 'all' ? (
            <p className="text-xs text-gray-600 mt-1">Try adjusting your filters</p>
          ) : null}
        </div>
      )}

      <div className={
        layout === 'grid'
          ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4'
          : 'space-y-2'
      }>
        {filtered.map((agent) => (
          <AgentCard
            key={agent.id}
            agent={agent}
            onStart={onStart}
            onStop={onStop}
          />
        ))}
      </div>
    </div>
  );
}
