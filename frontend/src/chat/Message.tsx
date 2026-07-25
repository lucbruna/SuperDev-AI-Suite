import React, { useState } from 'react';
import { Message as MessageType } from '../types/chat';
import MarkdownViewer from './MarkdownViewer';

interface MessageProps {
  message: MessageType;
}

export default function Message({ message }: MessageProps) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  const copyContent = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const time = new Date(message.timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });

  if (isSystem) {
    return (
      <div className="flex justify-center py-2">
        <div className="rounded-lg bg-gray-800/50 px-4 py-2 text-xs text-gray-500 italic">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-medium ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-purple-600 text-white'
        }`}
      >
        {isUser ? 'U' : 'AI'}
      </div>

      <div className={`group flex max-w-[80%] flex-col ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`rounded-2xl px-4 py-2.5 ${
            isUser
              ? 'bg-blue-600 text-white rounded-tr-sm'
              : 'bg-gray-800 text-gray-200 rounded-tl-sm'
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap text-sm">{message.content}</p>
          ) : (
            <MarkdownViewer content={message.content} />
          )}
        </div>

        <div className={`mt-1 flex items-center gap-2 px-1 ${isUser ? 'flex-row-reverse' : ''}`}>
          <span className="text-[10px] text-gray-500">{time}</span>
          {!isUser && (
            <span className="text-[10px] rounded bg-gray-800 px-1.5 py-0.5 text-gray-400">
              {message.model}
            </span>
          )}
          <button
            onClick={copyContent}
            className="opacity-0 group-hover:opacity-100 rounded p-0.5 text-gray-500 hover:text-gray-300 transition-opacity"
            title="Copy message"
          >
            {copied ? (
              <svg className="h-3.5 w-3.5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
