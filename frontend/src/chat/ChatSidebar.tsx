import React, { useState } from 'react';
import { Conversation } from '../types/chat';
import ConversationList from './ConversationList';

interface ChatSidebarProps {
  conversations: Conversation[];
  activeConversationId?: string;
  collapsed: boolean;
  onToggleCollapse: () => void;
  onSelect: (conv: Conversation) => void;
  onCreate: () => void;
  onDelete: (id: string) => void;
}

export default function ChatSidebar({
  conversations,
  activeConversationId,
  collapsed,
  onToggleCollapse,
  onSelect,
  onCreate,
  onDelete,
}: ChatSidebarProps) {
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = conversations.filter((c) =>
    c.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (collapsed) {
    return (
      <div className="flex flex-col items-center border-r border-gray-800 bg-gray-950 py-4">
        <button
          onClick={onToggleCollapse}
          className="mb-4 rounded-md p-2 text-gray-400 hover:bg-gray-800 hover:text-white"
          title="Expand sidebar"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
          </svg>
        </button>
        <button
          onClick={onCreate}
          className="rounded-md p-2 text-gray-400 hover:bg-gray-800 hover:text-white"
          title="New chat"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        </button>
      </div>
    );
  }

  return (
    <div className="flex w-72 flex-col border-r border-gray-800 bg-gray-950">
      <div className="flex items-center justify-between border-b border-gray-800 p-3">
        <h2 className="text-sm font-semibold text-gray-300">Conversations</h2>
        <button
          onClick={onToggleCollapse}
          className="rounded-md p-1 text-gray-500 hover:bg-gray-800 hover:text-gray-300"
          title="Collapse sidebar"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
          </svg>
        </button>
      </div>

      <div className="border-b border-gray-800 p-3">
        <button
          onClick={onCreate}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-500"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Chat
        </button>
      </div>

      <div className="border-b border-gray-800 p-3">
        <div className="relative">
          <svg
            className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search conversations..."
            className="w-full rounded-md border border-gray-700 bg-gray-900 py-1.5 pl-9 pr-3 text-sm text-gray-300 placeholder-gray-500 focus:border-blue-500 focus:outline-none"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {filtered.length === 0 ? (
          <div className="p-4 text-center text-sm text-gray-500">
            {searchQuery ? 'No conversations found' : 'No conversations yet'}
          </div>
        ) : (
          <ConversationList
            conversations={filtered}
            activeId={activeConversationId}
            onSelect={onSelect}
            onDelete={onDelete}
          />
        )}
      </div>
    </div>
  );
}
