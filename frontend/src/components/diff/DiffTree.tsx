"use client";

interface DiffTreeProps {
  files: { path: string; status: "added" | "modified" | "deleted"; changes: number }[];
  selectedPath: string | null;
  onSelect: (path: string) => void;
}

export function DiffTree({ files, selectedPath, onSelect }: DiffTreeProps) {
  const statusColor = (status: string) => {
    if (status === "added") return "text-green-600";
    if (status === "deleted") return "text-red-600";
    return "text-yellow-600";
  };

  const grouped: Record<string, typeof files> = {};
  for (const f of files) {
    const dir = f.path.includes("/") ? f.path.split("/")[0] : "root";
    if (!grouped[dir]) grouped[dir] = [];
    grouped[dir].push(f);
  }

  return (
    <div className="rounded-xl border bg-white p-3 dark:border-surface-700 dark:bg-surface-900">
      <h3 className="mb-2 text-xs font-semibold text-surface-500 uppercase">Changed Files</h3>
      {Object.entries(grouped).map(([dir, dirFiles]) => (
        <div key={dir}>
          <p className="px-2 py-1 text-xs font-medium text-surface-400">{dir}/</p>
          {dirFiles.map((f) => (
            <div
              key={f.path}
              onClick={() => onSelect(f.path)}
              className={`flex cursor-pointer items-center gap-2 rounded px-2 py-1 text-xs hover:bg-surface-100 dark:hover:bg-surface-800 ${selectedPath === f.path ? "bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300" : "text-surface-700 dark:text-surface-300"}`}
            >
              <span className={`font-mono ${statusColor(f.status)}`}>{f.status === "added" ? "A" : f.status === "deleted" ? "D" : "M"}</span>
              <span className="flex-1 truncate font-mono">{f.path}</span>
              <span className="text-surface-400">{f.changes}</span>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}