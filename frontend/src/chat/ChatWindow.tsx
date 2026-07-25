import React, { useRef, useEffect } from 'react';
import { Conversation, Message, StreamChunk } from '../types/chat';
import ChatSidebar from './ChatSidebar';
import ConversationView from './Conversation';
import PromptInput from './PromptInput';
import PromptToolbar from './PromptToolbar';

interface ChatWindowProps {
  conversations: Conversation[];
  activeConversation: Conversation | null;
  isStreaming: boolean;
  streamingContent: string;
  loading: boolean;
  error: string | null;
  onSelectConversation: (conv: Conversation) => void;
  onCreateConversation: () => void;
  onDeleteConversation: (id: string) => void;
  onSendMessage: (text: string) => void;
  onStopStreaming: () => void;
  onModelChange: (model: string) => void;
  onProviderChange: (provider: string) => void;
  onTemperatureChange: (temp: number) => void;
  onMaxTokensChange: (tokens: number) => void;
  onClearChat: () => void;
}

export default function ChatWindow({
  conversations,
  activeConversation,
  isStreaming,
  streamingContent,
  loading,
  error,
  onSelectConversation,
  onCreateConversation,
  onDeleteConversation,
  onSendMessage,
  onStopStreaming,
  onModelChange,
  onProviderChange,
  onTemperatureChange,
  onMaxTokensChange,
  onClearChat,
}: ChatWindowProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeConversation?.messages, streamingContent]);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center bg-gray-900">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
          <p className="text-sm text-gray-400">Loading conversations...</p>
        </div>
      </div>
    );
  }

  if (error && conversations.length === 0) {
    return (
      <div className="flex h-full items-center justify-center bg-gray-900">
        <div className="flex flex-col items-center gap-3 text-center">
          <div className="rounded-full bg-red-500/10 p-3">
            <svg className="h-6 w-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p className="text-sm text-red-400">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="rounded-md bg-blue-600 px-4 py-1.5 text-sm text-white hover:bg-blue-500"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full bg-gray-900">
      <ChatSidebar
        conversations={conversations}
        activeConversationId={activeConversation?.id}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        onSelect={onSelectConversation}
        onCreate={onCreateConversation}
        onDelete={onDeleteConversation}
      />

      <div className="flex flex-1 flex-col overflow-hidden">
        {activeConversation ? (
          <>
            <PromptToolbar
              model={activeConversation.model}
              provider={activeConversation.provider}
              onModelChange={onModelChange}
              onProviderChange={onProviderChange}
              onTemperatureChange={onTemperatureChange}
              onMaxTokensChange={onMaxTokensChange}
              onClearChat={onClearChat}
            />
            <div className="flex-1 overflow-y-auto px-4 py-4">
              <ConversationView
                conversation={activeConversation}
                isStreaming={isStreaming}
                streamingContent={streamingContent}
              />
              <div ref={messagesEndRef} />
            </div>
            <PromptInput
              onSend={onSendMessage}
              onStop={onStopStreaming}
              isStreaming={isStreaming}
              disabled={false}
            />
          </>
        ) : (
          <div className="flex h-full items-center justify-center">
            <div className="text-center">
              <div className="mb-4 text-6xl">💬</div>
              <h2 className="mb-2 text-xl font-semibold text-gray-300">SuperDev Chat</h2>
              <p className="mb-6 text-sm text-gray-500">
                Select a conversation or create a new one to get started
              </p>
              <button
                onClick={onCreateConversation}
                className="rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-blue-500"
              >
                New Conversation
              </button>
            </div>
          </div>
        )}

        {error && (
          <div className="mx-4 mb-2 rounded-lg bg-red-500/10 px-4 py-2 text-sm text-red-400">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}
