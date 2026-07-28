import { EvalPanel } from "../../components/evals/EvalPanel";

export default function EvalsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-bold text-surface-900 dark:text-surface-50">Model Evals</h1>
        <p className="text-sm text-surface-500">Compare models side-by-side on latency, quality, and cost to justify smart routing decisions</p>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <EvalPanel />
        <div className="rounded-xl border dark:border-surface-700">
          <div className="border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
            <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">Available Models</span>
          </div>
          <div className="space-y-1 p-4">
            {["gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet", "claude-3-haiku", "gemini-1.5-pro", "gemini-1.5-flash"].map((m) => (
              <div key={m} className="flex items-center gap-2 rounded-lg bg-surface-50 px-3 py-2 text-xs dark:bg-surface-800 dark:text-surface-300">
                <span className="h-1.5 w-1.5 rounded-full bg-primary-500" />
                {m}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}