import { EvalHarnessPanel } from "../../components/eval-harness/EvalHarnessPanel";

export default function EvalHarnessPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-bold text-surface-900 dark:text-surface-50">LLM Eval Harness</h1>
        <p className="text-sm text-surface-500">Automated test suite for LLM quality — factual accuracy, code generation, safety, reasoning, and more</p>
      </div>
      <EvalHarnessPanel />
    </div>
  );
}