"use client";

interface PreviewProps {
  yaml: string;
}

export function Preview({ yaml }: PreviewProps) {
  const parsed = parsePreview(yaml);

  return (
    <div className="rounded-xl border dark:border-surface-700">
      <div className="border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
        <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">Preview</span>
      </div>
      <div className="p-4">
        {parsed.name && (
          <div className="mb-3">
            <p className="text-xs font-medium text-surface-400">Workflow</p>
            <p className="text-sm text-surface-900 dark:text-surface-50">{parsed.name}</p>
            {parsed.version && <p className="text-xs text-surface-500">v{parsed.version}</p>}
          </div>
        )}
        {parsed.steps && parsed.steps.length > 0 && (
          <div>
            <p className="mb-2 text-xs font-medium text-surface-400">Steps ({parsed.steps.length})</p>
            <div className="space-y-2">
              {parsed.steps.map((step: any, i: number) => (
                <div key={i} className="flex items-center gap-3 rounded-lg bg-surface-50 px-3 py-2 dark:bg-surface-800">
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary-100 text-xs font-medium text-primary-700 dark:bg-primary-900 dark:text-primary-300">{i + 1}</span>
                  <div>
                    <p className="text-xs font-medium text-surface-900 dark:text-surface-50 capitalize">{step.type || "unknown"}</p>
                    <p className="text-[11px] text-surface-500">{step.agent || step.environment || step.command || step.prompt?.slice(0, 40) || ""}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function parsePreview(text: string): { name?: string; version?: string; steps?: any[] } {
  const lines = text.split("\n");
  const result: any = {};
  let currentSteps: any[] = [];
  let currentStep: any = {};
  let inSteps = false;

  for (const line of lines) {
    if (!line.trim() || line.trim().startsWith("#")) continue;
    const indent = line.search(/\S/);
    const trimmed = line.trim();

    if (trimmed.startsWith("- ")) {
      if (inSteps && Object.keys(currentStep).length > 0) {
        currentSteps.push(currentStep);
        currentStep = {};
      }
      inSteps = true;
      const entry = trimmed.slice(2);
      const [k, ...v] = entry.split(":");
      if (v.length > 0) currentStep[k.trim()] = v.join(":").trim();
    } else if (indent === 2 && inSteps) {
      const [k, ...v] = trimmed.split(":");
      if (v.length > 0) currentStep[k.trim()] = v.join(":").trim();
    } else if (indent === 0 && !trimmed.startsWith("-")) {
      const [k, ...v] = trimmed.split(":");
      const val = v.join(":").trim();
      if (k === "steps") { inSteps = true; }
      else { result[k] = val; }
    }
  }
  if (inSteps && Object.keys(currentStep).length > 0) currentSteps.push(currentStep);
  if (currentSteps.length > 0) result.steps = currentSteps;
  return result;
}