import React, { useEffect, useState } from 'react';
import MarkdownViewer from './MarkdownViewer';

interface StreamingMessageProps {
  content: string;
  onStop?: () => void;
}

export default function StreamingMessage({ content, onStop }: StreamingMessageProps) {
  const [dots, setDots] = useState('');

  useEffect(() => {
    if (content) return;
    const interval = setInterval(() => {
      setDots((prev) => (prev.length >= 3 ? '' : prev + '.'));
    }, 400);
    return () => clearInterval(interval);
  }, [content]);

  return (
    <div className="flex gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-purple-600 text-sm font-medium text-white">
        AI
      </div>

      <div className="group flex max-w-[80%] flex-col items-start">
        <div className="rounded-2xl rounded-tl-sm bg-gray-800 px-4 py-2.5 text-gray-200">
          {content ? (
            <div className="streaming-content">
              <MarkdownViewer content={content} />
              <span className="inline-block h-4 w-0.5 animate-pulse bg-blue-400 ml-0.5" />
            </div>
          ) : (
            <div className="flex items-center gap-1 py-1">
              <span className="text-sm text-gray-400">Thinking</span>
              <span className="text-sm text-gray-400 w-6">{dots}</span>
            </div>
          )}
        </div>

        {onStop && (
          <div className="mt-1 flex items-center gap-2 px-1">
            <button
              onClick={onStop}
              className="flex items-center gap-1 rounded-md bg-red-500/10 px-2.5 py-1 text-xs text-red-400 hover:bg-red-500/20 transition-colors"
            >
              <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 24 24">
                <rect x="6" y="6" width="12" height="12" rx="1" />
              </svg>
              Stop generating
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
