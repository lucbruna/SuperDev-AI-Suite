import React, { useState } from 'react';
import { Conversation } from '../types/chat';

interface ConversationListProps {
  conversations: Conversation[];
  activeId?: string;
  onSelect: (conv: Conversation) => void;
  onDelete: (id: string) => void;
}

export default function ConversationList({
  conversations,
  activeId,
  onSelect,
  onDelete,
}: ConversationListProps) {
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  const formatDate = (ts: number) => {
    const d = new Date(ts);
    const now = new Date();
    const diff = now.getTime() - d.getTime();
    if (diff < 86400000) return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    if (diff < 604800000) return d.toLocaleDateString([], { weekday: 'short' });
    return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
  };

  const lastMessage = (conv: Conversation) => {
    const msg = conv.messages[conv.messages.length - 1];
    if (!msg) return 'No messages';
    const text = msg.content.replace(/<[^>]*>/g, '').replace(/\n/g, ' ');
    return text.length > 60 ? text.slice(0, 60) + '...' : text;
  };

  return (
    <div className="space-y-0.5 p-2">
      {conversations.map((conv) => (
        <div
          key={conv.id}
          onClick={() => onSelect(conv)}
          onMouseEnter={() => setHoveredId(conv.id)}
          onMouseLeave={() => setHoveredId(null)}
          className={`group relative cursor-pointer rounded-lg px-3 py-2.5 transition-colors ${
            conv.id === activeId
              ? 'bg-blue-600/20 border border-blue-500/30'
              : 'hover:bg-gray-800 border border-transparent'
          }`}
        >
          <div className="flex items-start justify-between gap-2">
            <h3 className="flex-1 truncate text-sm font-medium text-gray-200">
              {conv.title || 'Untitled'}
            </h3>
            <span className="shrink-0 text-xs text-gray-500">
              {formatDate(conv.updated_at)}
            </span>
          </div>
          <p className="mt-0.5 truncate text-xs text-gray-500">
            {lastMessage(conv)}
          </p>
          <div className="mt-1 flex items-center gap-2">
            <span className="text-[10px] rounded bg-gray-800 px-1.5 py-0.5 text-gray-400">
              {conv.model}
            </span>
          </div>

          {hoveredId === conv.id && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(conv.id);
              }}
              className="absolute right-2 top-2 rounded-md p-1 text-gray-500 opacity-0 group-hover:opacity-100 hover:bg-red-500/20 hover:text-red-400"
              title="Delete conversation"
            >
              <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          )}
        </div>
      ))}
    </div>
  );
}
