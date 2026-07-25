import React, { useState } from 'react';

interface CodePreviewProps {
  code: string;
  language?: string;
  maxHeight?: number;
}

export default function CodePreview({ code, language, maxHeight = 300 }: CodePreviewProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [copied, setCopied] = useState(false);

  const shouldCollapse = code.split('\n').length > 15 && collapsed;

  const copyCode = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="group relative my-2 overflow-hidden rounded-lg border border-gray-700 bg-gray-950">
      <div className="flex items-center justify-between bg-gray-900 px-3 py-1.5">
        <div className="flex items-center gap-2">
          {language && (
            <span className="rounded bg-blue-600/20 px-1.5 py-0.5 text-[10px] font-medium text-blue-400">
              {language}
            </span>
          )}
          <span className="text-[10px] text-gray-500">
            {code.split('\n').length} lines
          </span>
        </div>
        <div className="flex items-center gap-1">
          {shouldCollapse && (
            <button
              onClick={() => setCollapsed(false)}
              className="rounded px-1.5 py-0.5 text-[10px] text-gray-400 hover:bg-gray-800"
            >
              Expand
            </button>
          )}
          <button
            onClick={copyCode}
            className="rounded p-1 text-gray-500 hover:bg-gray-800 hover:text-gray-300 transition-colors"
            title="Copy code"
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
      <div className="overflow-x-auto" style={{ maxHeight: shouldCollapse ? maxHeight : undefined }}>
        <pre className="relative p-3 text-xs leading-relaxed">
          <code className="text-gray-300">
            {code.split('\n').map((line, i) => (
              <div key={i} className="flex">
                <span className="mr-4 select-none text-gray-600 w-8 text-right shrink-0">{i + 1}</span>
                <span
                  dangerouslySetInnerHTML={{
                    __html: highlightLine(line, language),
                  }}
                />
              </div>
            ))}
          </code>
        </pre>
        {shouldCollapse && (
          <div className="absolute bottom-0 left-0 right-0 flex justify-center bg-gradient-to-t from-gray-950 pt-8 pb-2">
            <button
              onClick={() => setCollapsed(false)}
              className="rounded-lg bg-gray-800 px-4 py-1 text-xs text-gray-400 hover:bg-gray-700"
            >
              Show all {code.split('\n').length} lines
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function highlightLine(line: string, lang?: string): string {
  let escaped = line
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  escaped = escaped
    .replace(/\/\/.*$/g, '<span class="hljs-comment">$&</span>')
    .replace(/\/\*[\s\S]*?\*\//g, '<span class="hljs-comment">$&</span>')
    .replace(/("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|`(?:[^`\\]|\\.)*`)/g, '<span class="hljs-string">$1</span>')
    .replace(/\b(const|let|var|function|return|if|else|for|while|class|import|export|from|async|await|new|this|try|catch|throw|def|int|float|bool|true|false|null|undefined)\b/g, '<span class="hljs-keyword">$1</span>')
    .replace(/\b(\d+\.?\d*)\b/g, '<span class="hljs-number">$1</span>');

  return escaped;
}
