"use client";

interface ValidatorProps {
  errors: string[];
  onFix: () => void;
}

export function Validator({ errors, onFix }: ValidatorProps) {
  if (errors.length === 0) {
    return (
      <div className="rounded-xl border border-green-700 bg-green-950/30 p-4">
        <p className="text-xs font-medium text-green-400">✓ Valid — no issues found</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-red-800 bg-red-950/30 p-4">
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold text-red-400">{errors.length} error{errors.length > 1 ? "s" : ""}</p>
        <button onClick={onFix} className="rounded bg-red-800 px-2 py-1 text-xs text-red-200 hover:bg-red-700">Reset to default</button>
      </div>
      <ul className="mt-2 space-y-1">
        {errors.map((err, i) => (
          <li key={i} className="flex items-start gap-2 text-xs text-red-300">
            <span>•</span>
            <span>{err}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}