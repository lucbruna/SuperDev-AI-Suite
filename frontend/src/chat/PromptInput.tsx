import React, { useRef, useState, useCallback, useEffect } from 'react';

interface PromptInputProps {
  onSend: (text: string) => void;
  onStop?: () => void;
  isStreaming: boolean;
  disabled?: boolean;
}

export default function PromptInput({
  onSend,
  onStop,
  isStreaming,
  disabled,
}: PromptInputProps) {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const autoResize = useCallback(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 200) + 'px';
  }, []);

  useEffect(() => {
    autoResize();
  }, [text, autoResize]);

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed || isStreaming) return;
    onSend(trimmed);
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileClick = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.click();
  };

  const insertCodeBlock = () => {
    const ta = textareaRef.current;
    if (!ta) return;
    const start = ta.selectionStart;
    const end = ta.selectionEnd;
    const code = '```\n' + text.slice(start, end) + '\n```';
    const newText = text.slice(0, start) + code + text.slice(end);
    setText(newText);
    setTimeout(() => {
      ta.focus();
      ta.selectionStart = ta.selectionEnd = start + 4;
    }, 0);
  };

  const hasText = text.trim().length > 0;

  return (
    <div className="border-t border-gray-800 bg-gray-950 px-4 py-3">
      <div className="mx-auto flex max-w-4xl flex-col gap-2">
        <div className="flex items-end gap-2 rounded-xl border border-gray-700 bg-gray-900 px-3 py-2 focus-within:border-blue-500/50 transition-colors">
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={handleFileClick}
              disabled={disabled || isStreaming}
              className="rounded-md p-1.5 text-gray-500 hover:bg-gray-800 hover:text-gray-300 disabled:opacity-40"
              title="Attach file"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
              </svg>
            </button>
            <button
              type="button"
              onClick={insertCodeBlock}
              disabled={disabled || isStreaming}
              className="rounded-md p-1.5 text-gray-500 hover:bg-gray-800 hover:text-gray-300 disabled:opacity-40"
              title="Insert code block"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
            </button>
          </div>

          <textarea
            ref={textareaRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message... (Shift+Enter for new line)"
            rows={1}
            disabled={disabled}
            className="max-h-[200px] min-h-[24px] flex-1 resize-none bg-transparent text-sm text-gray-200 placeholder-gray-500 focus:outline-none disabled:opacity-50"
          />

          {isStreaming && onStop ? (
            <button
              onClick={onStop}
              className="flex shrink-0 items-center gap-1.5 rounded-lg bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-500"
            >
              <svg className="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 24 24">
                <rect x="6" y="6" width="12" height="12" rx="1" />
              </svg>
              Stop
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!hasText || disabled}
              className={`flex shrink-0 items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                hasText
                  ? 'bg-blue-600 text-white hover:bg-blue-500'
                  : 'bg-gray-800 text-gray-500 cursor-not-allowed'
              }`}
            >
              <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              Send
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
