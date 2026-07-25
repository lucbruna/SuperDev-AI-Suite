import React from 'react';
import { AgentStatus as AgentStatusType } from '../types/agent';

const STATUS_CONFIG: Record<AgentStatusType, { color: string; label: string }> = {
  online: { color: 'bg-green-500', label: 'Online' },
  busy: { color: 'bg-yellow-500', label: 'Busy' },
  error: { color: 'bg-red-500', label: 'Error' },
  offline: { color: 'bg-gray-500', label: 'Offline' },
};

interface AgentStatusProps {
  status: AgentStatusType;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const SIZE_CLASSES = {
  sm: 'h-1.5 w-1.5',
  md: 'h-2 w-2',
  lg: 'h-2.5 w-2.5',
};

export default function AgentStatus({ status, showLabel = true, size = 'md' }: AgentStatusProps) {
  const config = STATUS_CONFIG[status];

  return (
    <div className="flex items-center gap-1.5">
      <span
        className={`inline-block rounded-full ${SIZE_CLASSES[size]} ${config.color}`}
        title={config.label}
      />
      {showLabel && (
        <span className="text-xs text-gray-400">{config.label}</span>
      )}
    </div>
  );
}
