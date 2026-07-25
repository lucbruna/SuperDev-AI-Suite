import React from 'react';
import { Conversation } from '../types/chat';
import Message from './Message';
import StreamingMessage from './StreamingMessage';

interface ConversationViewProps {
  conversation: Conversation;
  isStreaming: boolean;
  streamingContent: string;
}

export default function ConversationView({
  conversation,
  isStreaming,
  streamingContent,
}: ConversationViewProps) {
  return (
    <div className="space-y-4">
      {conversation.messages.length === 0 && !isStreaming && (
        <div className="flex h-full items-center justify-center py-20">
          <div className="text-center">
            <p className="text-sm text-gray-500">
              Start a conversation by typing a message below
            </p>
          </div>
        </div>
      )}

      {conversation.messages.map((msg) => (
        <Message key={msg.id} message={msg} />
      ))}

      {isStreaming && <StreamingMessage content={streamingContent} />}
    </div>
  );
}
