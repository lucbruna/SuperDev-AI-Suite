"use client";

import { useState } from "react";

interface DiffFile {
  path: string;
  status: "added" | "modified" | "deleted";
  hunks: { oldStart: number; newStart: number; lines: { type: "add" | "del" | "ctx"; content: string }[] }[];
}

const MOCK_DIFF: DiffFile[] = [
  {
    path: "src/main.py",
    status: "modified",
    hunks: [{
      oldStart: 10, newStart: 10,
      lines: [
        { type: "ctx", content: "def process(data):" },
        { type: "ctx", content: "    result = []" },
        { type: "del", content: "    for item in data:" },
        { type: "add", content: "    for item in data.get('items', []):" },
        { type: "del", content: "        result.append(transform(item))" },
        { type: "add", content: "        transformed = transform(item)" },
        { type: "add", content: "        if transformed is not None:" },
        { type: "add", content: "            result.append(transformed)" },
        { type: "ctx", content: "    return result" },
      ],
    }],
  },
  {
    path: "src/utils.py",
    status: "added",
    hunks: [{
      oldStart: 0, newStart: 1,
      lines: [
        { type: "add", content: "def validate_input(data: dict) -> bool:" },
        { type: "add", content: "    return 'items' in data and len(data['items']) > 0" },
        { type: "add", content: "" },
        { type: "add", content: "def format_output(data: list) -> str:" },
        { type: "add", content: "    return json.dumps(data, indent=2)" },
      ],
    }],
  },
  {
    path: "src/legacy.py",
    status: "deleted",
    hunks: [{
      oldStart: 1, newStart: 0,
      lines: [
        { type: "del", content: "# Deprecated module" },
        { type: "del", content: "def old_process(data):" },
        { type: "del", content: "    pass" },
      ],
    }],
  },
];

export function DiffViewer() {
  const [files] = useState(MOCK_DIFF);
  const [expanded, setExpanded] = useState<string>(MOCK_DIFF[0]?.path || "");
  const [accepted, setAccepted] = useState<Set<string>>(new Set());
  const [rejected, setRejected] = useState<Set<string>>(new Set());
  const [viewMode, setViewMode] = useState<"unified" | "split">("unified");

  const toggleFile = (path: string) => setExpanded(expanded === path ? "" : path);

  const acceptFile = (path: string) => {
    setAccepted(new Set([...accepted, path]));
    setRejected(new Set([...rejected].filter((r) => r !== path)));
  };

  const rejectFile = (path: string) => {
    setRejected(new Set([...rejected, path]));
    setAccepted(new Set([...accepted].filter((a) => a !== path)));
  };

  const totalChanges = files.reduce((s, f) => s + f.hunks.reduce((h, hk) => h + hk.lines.filter((l) => l.type !== "ctx").length, 0), 0);

  return (
    <div className="rounded-xl border bg-white dark:border-surface-700 dark:bg-surface-900">
      <div className="flex items-center justify-between border-b px-4 py-3 dark:border-surface-700">
        <div className="flex items-center gap-3">
          <h3 className="text-sm font-semibold text-surface-900 dark:text-surface-50">Changes Preview</h3>
          <span className="text-xs text-surface-500">{files.length} files | {totalChanges} changes</span>
          <span className={`rounded-full px-2 py-0.5 text-xs ${accepted.size === files.length ? "bg-green-100 text-green-700" : "bg-surface-100 text-surface-500"}`}>
            {accepted.size}/{files.length} accepted
          </span>
        </div>
        <div className="flex gap-1">
          <button onClick={() => setViewMode("unified")} className={`rounded px-2 py-1 text-xs ${viewMode === "unified" ? "bg-primary-600 text-white" : "bg-surface-200 text-surface-600"}`}>Unified</button>
          <button onClick={() => setViewMode("split")} className={`rounded px-2 py-1 text-xs ${viewMode === "split" ? "bg-primary-600 text-white" : "bg-surface-200 text-surface-600"}`}>Split</button>
        </div>
      </div>

      <div className="divide-y dark:divide-surface-700">
        {files.map((file) => (
          <div key={file.path}>
            <div
              onClick={() => toggleFile(file.path)}
              className="flex items-center justify-between px-4 py-2.5 cursor-pointer hover:bg-surface-50 dark:hover:bg-surface-800/50"
            >
              <div className="flex items-center gap-2">
                <span className="text-xs text-surface-400">{expanded === file.path ? "▼" : "▶"}</span>
                <span className={`rounded px-1.5 py-0.5 text-xs font-medium ${file.status === "added" ? "bg-green-100 text-green-700" : file.status === "deleted" ? "bg-red-100 text-red-700" : "bg-yellow-100 text-yellow-700"}`}>
                  {file.status}
                </span>
                <span className="text-sm font-mono text-surface-700 dark:text-surface-300">{file.path}</span>
              </div>
              <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                <button onClick={() => acceptFile(file.path)} className={`rounded px-2 py-1 text-xs ${accepted.has(file.path) ? "bg-green-500 text-white" : "bg-surface-200 text-surface-600 hover:bg-green-100"}`}>✓ Accept</button>
                <button onClick={() => rejectFile(file.path)} className={`rounded px-2 py-1 text-xs ${rejected.has(file.path) ? "bg-red-500 text-white" : "bg-surface-200 text-surface-600 hover:bg-red-100"}`}>✗ Reject</button>
              </div>
            </div>
            {expanded === file.path && (
              <div className="border-t bg-surface-50 px-4 py-2 font-mono text-xs dark:border-surface-700 dark:bg-surface-950">
                {file.hunks.map((hunk, hi) => (
                  <div key={hi}>
                    <div className="py-1 text-surface-400">@@ -{hunk.oldStart} +{hunk.newStart} @@</div>
                    {hunk.lines.map((line, li) => (
                      <div key={li} className={`flex ${line.type === "add" ? "bg-green-50 text-green-800 dark:bg-green-950 dark:text-green-300" : line.type === "del" ? "bg-red-50 text-red-800 dark:bg-red-950 dark:text-red-300" : "text-surface-600 dark:text-surface-400"}`}>
                        <span className="w-6 shrink-0 text-right text-surface-300">{line.type === "add" ? "+" : line.type === "del" ? "-" : " "}</span>
                        <span className="flex-1 px-2">{line.content}</span>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="flex items-center justify-between border-t px-4 py-3 dark:border-surface-700">
        <div className="flex gap-2">
          <button className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700">Apply All</button>
          <button className="rounded-lg bg-surface-200 px-4 py-2 text-sm font-medium text-surface-700 hover:bg-surface-300 dark:bg-surface-700 dark:text-surface-300">Apply Selected</button>
        </div>
        <button className="text-sm text-surface-500 hover:text-red-600">Discard All</button>
      </div>
    </div>
  );
}