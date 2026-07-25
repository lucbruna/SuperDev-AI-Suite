"use client";

import { useState, useCallback, useRef, useMemo } from "react";
import { cn } from "@/utils/cn";

const languages = [
  "javascript", "typescript", "python", "html", "css", "json", "yaml", "markdown", "sql", "bash",
];

const KEYWORDS: Record<string, string[]> = {
  javascript: ["const", "let", "var", "function", "return", "if", "else", "for", "while", "import", "export", "from", "async", "await", "class", "new", "this", "throw", "try", "catch"],
  typescript: ["const", "let", "var", "function", "return", "if", "else", "for", "while", "import", "export", "from", "async", "await", "class", "new", "this", "throw", "try", "catch", "interface", "type", "enum", "implements", "extends"],
  python: ["def", "return", "if", "else", "elif", "for", "while", "import", "from", "as", "class", "try", "except", "finally", "with", "yield", "lambda", "pass", "break", "continue", "and", "or", "not", "in", "is", "None", "True", "False"],
  html: ["html", "head", "body", "div", "span", "script", "style", "link", "meta", "title"],
  css: ["import", "media", "keyframes", "important"],
  json: [],
  yaml: [],
  markdown: [],
  sql: ["SELECT", "FROM", "WHERE", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER", "TABLE", "INTO", "VALUES", "SET", "AND", "OR", "NOT", "IN", "LIKE", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER", "ON", "GROUP", "BY", "ORDER", "HAVING", "LIMIT", "OFFSET", "AS", "DISTINCT", "COUNT", "SUM", "AVG", "MAX", "MIN"],
  bash: ["if", "then", "else", "elif", "fi", "for", "while", "do", "done", "case", "esac", "function", "return", "exit", "echo", "export", "source"],
};

function tokenize(code: string, language: string): { text: string; className: string }[] {
  const keywords = KEYWORDS[language] ?? [];
  const tokenRegex = /("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\b\d+\.?\d*\b|\b[a-zA-Z_$][\w$]*\b|#[^\n]*|\/\/[^\n]*|\/\*[\s\S]*?\*\/|.)/g;
  const tokens: { text: string; className: string }[] = [];
  let match;

  while ((match = tokenRegex.exec(code)) !== null) {
    const token = match[0];
    if (token.startsWith('"') || token.startsWith("'")) {
      tokens.push({ text: token, className: "text-emerald-600 dark:text-emerald-400" });
    } else if (/^\d/.test(token) && !isNaN(Number(token))) {
      tokens.push({ text: token, className: "text-amber-600 dark:text-amber-400" });
    } else if (keywords.includes(token)) {
      tokens.push({ text: token, className: "text-blue-600 dark:text-blue-400 font-semibold" });
    } else if (token.startsWith("#") || token.startsWith("//") || token.startsWith("/*")) {
      tokens.push({ text: token, className: "text-surface-400 italic" });
    } else {
      tokens.push({ text: token, className: "text-surface-900 dark:text-surface-100" });
    }
  }

  return tokens;
}

interface MonacoEditorProps {
  language?: string;
  value?: string;
  onChange?: (value: string) => void;
  readOnly?: boolean;
  className?: string;
}

export function MonacoEditor({
  language = "typescript",
  value = "",
  onChange,
  readOnly = false,
  className,
}: MonacoEditorProps) {
  const [currentLang, setCurrentLang] = useState(language);
  const [theme, setTheme] = useState<"light" | "dark">("dark");
  const [fontSize, setFontSize] = useState(14);
  const [cursorLine, setCursorLine] = useState(1);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const lines = value.split("\n");
  const lineCount = lines.length;

  const handleKeyUp = useCallback(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    const pos = ta.selectionStart;
    const before = value.slice(0, pos);
    setCursorLine(before.split("\n").length);
  }, [value]);

  const handleScroll = useCallback(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    const lineNumbers = ta.parentElement?.querySelector(".line-numbers");
    if (lineNumbers) {
      (lineNumbers as HTMLDivElement).scrollTop = ta.scrollTop;
    }
  }, []);

  const renderedLines = useMemo(() => {
    return lines.map((line, i) => {
      const tokens = tokenize(line, currentLang);
      return (
        <div key={i} className="flex">
          <span
            className="mr-0 inline-block w-12 shrink-0 select-none text-right text-xs leading-6 text-surface-400"
          >
            {i + 1}
          </span>
          <span className="flex-1 whitespace-pre font-mono text-sm leading-6">
            {tokens.length > 0
              ? tokens.map((t, j) => (
                  <span key={j} className={t.className}>
                    {t.text}
                  </span>
                ))
              : <span className="text-surface-900 dark:text-surface-100">&nbsp;</span>}
          </span>
        </div>
      );
    });
  }, [lines, currentLang]);

  return (
    <div className={cn("flex flex-col rounded-xl border border-surface-200 dark:border-surface-700", className)}>
      <div className="flex items-center gap-3 border-b border-surface-200 bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
        <select
          value={currentLang}
          onChange={(e) => setCurrentLang(e.target.value)}
          className="rounded-md border border-surface-300 bg-white px-2 py-1 text-xs font-medium text-surface-700 focus:outline-none focus:ring-1 focus:ring-primary-500 dark:border-surface-600 dark:bg-surface-700 dark:text-surface-200"
        >
          {languages.map((l) => (
            <option key={l} value={l}>{l}</option>
          ))}
        </select>

        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="rounded-md border border-surface-300 bg-white px-2 py-1 text-xs font-medium text-surface-700 hover:bg-surface-100 dark:border-surface-600 dark:bg-surface-700 dark:text-surface-200 dark:hover:bg-surface-600"
        >
          {theme === "dark" ? "Light" : "Dark"}
        </button>

        <div className="flex items-center gap-2">
          <span className="text-[11px] text-surface-400">A</span>
          <input
            type="range"
            min="10"
            max="24"
            value={fontSize}
            onChange={(e) => setFontSize(Number(e.target.value))}
            className="h-1 w-16 cursor-pointer appearance-none rounded bg-surface-300 accent-primary-500 dark:bg-surface-600"
          />
          <span className="text-sm text-surface-400">A</span>
        </div>

        <div className="ml-auto flex items-center gap-3 text-[11px] text-surface-400">
          <span>Ln {cursorLine}</span>
          <span>{currentLang}</span>
        </div>
      </div>

      <div
        className={cn(
          "relative flex overflow-hidden",
          theme === "dark" ? "bg-surface-950" : "bg-white",
        )}
        style={{ fontSize: `${fontSize}px` }}
      >
        <div
          className="line-numbers min-w-[3.5rem] shrink-0 select-none overflow-hidden border-r border-surface-200 bg-surface-50 py-3 text-right dark:border-surface-700 dark:bg-surface-900"
          aria-hidden
        >
          {lines.map((_, i) => (
            <div
              key={i}
              className={cn(
                "pr-3 font-mono text-xs leading-6",
                cursorLine === i + 1
                  ? "text-primary-600 dark:text-primary-400"
                  : "text-surface-400",
              )}
            >
              {i + 1}
            </div>
          ))}
        </div>

        <div className="relative flex-1">
          <pre
            className="pointer-events-none absolute inset-0 overflow-hidden py-3 pl-4"
            aria-hidden
          >
            {renderedLines}
          </pre>
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => onChange?.(e.target.value)}
            onKeyUp={handleKeyUp}
            onScroll={handleScroll}
            readOnly={readOnly}
            spellCheck={false}
            className={cn(
              "relative min-h-[200px] w-full resize-none bg-transparent py-3 pl-4 font-mono text-sm leading-6 text-transparent caret-surface-700 outline-none dark:caret-surface-200",
              readOnly && "cursor-default",
            )}
            style={{ fontSize: `${fontSize}px` }}
            aria-label="Code editor"
          />
        </div>
      </div>
    </div>
  );
}
