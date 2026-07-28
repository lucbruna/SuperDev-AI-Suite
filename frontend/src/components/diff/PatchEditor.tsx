"use client";

import { useState } from "react";

interface HunkLine {
  type: "add" | "del" | "ctx";
  content: string;
  oldLine: number;
  newLine: number;
}

interface Hunk {
  oldStart: number;
  newStart: number;
  lines: HunkLine[];
}

interface DiffFile {
  path: string;
  status: "added" | "modified" | "deleted";
  hunks: Hunk[];
}

export function PatchEditor() {
  const [diffFiles] = useState<DiffFile[]>([
    { path: "src/main.py", status: "modified", hunks: [{ oldStart: 10, newStart: 10, lines: [
      { type: "ctx", content: "def main():", oldLine: 10, newLine: 10 },
      { type: "ctx", content: "    parser = argparse.ArgumentParser()", oldLine: 11, newLine: 11 },
      { type: "del", content: "    parser.add_argument('--name')", oldLine: 12, newLine: 0 },
      { type: "add", content: "    parser.add_argument('--name', required=True, help='User name')", oldLine: 0, newLine: 12 },
      { type: "add", content: "    parser.add_argument('--verbose', action='store_true')", oldLine: 0, newLine: 13 },
      { type: "ctx", content: "    args = parser.parse_args()", oldLine: 13, newLine: 14 },
    ]}]},
  ]);

  const [patches, setPatches] = useState<Record<string, string>>({});

  const applyPatch = (filepath: string) => {
    setPatches((prev) => ({ ...prev, [filepath]: "applied" }));
  };

  const rejectPatch = (filepath: string) => {
    setPatches((prev) => ({ ...prev, [filepath]: "rejected" }));
  };

  return (
    <div className="rounded-xl border dark:border-surface-700">
      <div className="border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
        <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">Patch Editor</span>
      </div>
      <div className="divide-y dark:divide-surface-700">
        {diffFiles.map((file) => (
          <div key={file.path} className="p-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-surface-700 dark:text-surface-300">{file.path}</span>
                <span className={`rounded px-1.5 py-0.5 text-[9px] ${file.status === "added" ? "bg-green-100 text-green-700" : file.status === "deleted" ? "bg-red-100 text-red-700" : "bg-yellow-100 text-yellow-700"}`}>{file.status}</span>
              </div>
              <div className="flex gap-1">
                {patches[file.path] === "applied" ? (
                  <span className="text-[10px] text-green-500">Applied</span>
                ) : patches[file.path] === "rejected" ? (
                  <span className="text-[10px] text-red-500">Rejected</span>
                ) : (
                  <>
                    <button onClick={() => applyPatch(file.path)} className="rounded bg-green-600 px-2 py-1 text-[9px] text-white hover:bg-green-700">Apply</button>
                    <button onClick={() => rejectPatch(file.path)} className="rounded bg-red-600 px-2 py-1 text-[9px] text-white hover:bg-red-700">Reject</button>
                  </>
                )}
              </div>
            </div>
            <div className="mt-2 rounded-lg bg-black p-2 font-mono text-[10px]">
              {file.hunks.map((hunk, hi) => (
                <div key={hi}>
                  <p className="text-surface-500">@@ -{hunk.oldStart} +{hunk.newStart} @@</p>
                  {hunk.lines.map((line, li) => (
                    <p key={li} className={`${line.type === "add" ? "text-green-400" : line.type === "del" ? "text-red-400" : "text-gray-400"}`}>
                      {line.type === "add" ? "+" : line.type === "del" ? "-" : " "}{line.content}
                    </p>
                  ))}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}