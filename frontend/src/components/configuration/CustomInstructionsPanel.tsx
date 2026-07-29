"use client";

import { useState, useEffect } from "react";
import { api } from "@/utils/api-fetch";

const DEFAULT_RULES = [
  { id: "lang-python", pattern: "*.py", instruction: "Use type hints, follow PEP 8, max line length 120", enabled: true },
  { id: "lang-ts", pattern: "*.ts", instruction: "Use strict TypeScript, prefer interfaces over types", enabled: true },
  { id: "lang-tsx", pattern: "*.tsx", instruction: "Use React functional components with hooks", enabled: true },
  { id: "testing", pattern: "test_*", instruction: "Write tests first (TDD), aim for >80% coverage", enabled: false },
  { id: "security", pattern: "*", instruction: "Never hardcode secrets, validate all user input", enabled: true },
  { id: "docs", pattern: "*.py", instruction: "Write docstrings for all public functions", enabled: true },
];

export function CustomInstructionsPanel() {
  const [rules, setRules] = useState<any[]>(DEFAULT_RULES);
  const [saved, setSaved] = useState(false);
  const [newPattern, setNewPattern] = useState("");
  const [newInstruction, setNewInstruction] = useState("");

  useEffect(() => {
    api.get<any>("/api/configuration/rules").then(d => {
      if (d.rules) setRules(d.rules.map((r: any) => typeof r === "string" ? { id: "custom", pattern: "*", instruction: r, enabled: true } : { ...r, enabled: r.enabled ?? true }));
    }).catch(() => {});
  }, []);

  const toggleRule = (id: string) => {
    setRules(prev => prev.map(r => r.id === id ? { ...r, enabled: !r.enabled } : r));
    setSaved(false);
  };

  const addRule = () => {
    if (!newPattern.trim() || !newInstruction.trim()) return;
    setRules(prev => [...prev, { id: `custom_${Date.now()}`, pattern: newPattern, instruction: newInstruction, enabled: true }]);
    setNewPattern(""); setNewInstruction("");
    setSaved(false);
  };

  const removeRule = (id: string) => {
    setRules(prev => prev.filter(r => r.id !== id));
    setSaved(false);
  };

  const save = async () => {
    try {
      await api.put("/api/configuration/rules", { rules });
      setSaved(true);
    } catch {}
  };

  const preview = rules.filter(r => r.enabled).map(r => `- **${r.pattern}**: ${r.instruction}`).join("\n");

  return (
    <div className="space-y-4">
      <div className="rounded-xl border dark:border-surface-700">
        <div className="border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
          <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">Project Rules ({rules.filter(r => r.enabled).length} active)</span>
        </div>
        <div className="divide-y dark:divide-surface-700">
          {rules.map((rule) => (
            <div key={rule.id} className="flex items-center justify-between px-4 py-2.5">
              <div className="flex items-center gap-3">
                <input type="checkbox" checked={rule.enabled} onChange={() => toggleRule(rule.id)} className="h-3.5 w-3.5 rounded border-surface-300 text-primary-600" />
                <div>
                  <div className="flex items-center gap-2">
                    <span className="rounded bg-primary-100 px-1.5 py-0.5 text-[9px] font-mono text-primary-700 dark:bg-primary-900 dark:text-primary-300">{rule.pattern}</span>
                    <span className="text-xs text-surface-700 dark:text-surface-200">{rule.instruction}</span>
                  </div>
                </div>
              </div>
              <button onClick={() => removeRule(rule.id)} className="text-[9px] text-red-500 hover:text-red-700">x</button>
            </div>
          ))}
        </div>
      </div>

      <div className="flex gap-2">
        <input value={newPattern} onChange={(e) => setNewPattern(e.target.value)} placeholder="File pattern (e.g. *.tsx)" className="w-32 rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800" />
        <input value={newInstruction} onChange={(e) => setNewInstruction(e.target.value)} onKeyDown={(e) => e.key === "Enter" && addRule()} placeholder="Instruction for AI..." className="flex-1 rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800" />
        <button onClick={addRule} disabled={!newPattern.trim() || !newInstruction.trim()} className="rounded-lg bg-primary-600 px-3 py-2 text-xs font-medium text-white hover:bg-primary-700 disabled:opacity-40">Add</button>
      </div>

      <div className="rounded-xl border bg-surface-50 p-3 dark:border-surface-700 dark:bg-surface-800">
        <p className="mb-1 text-[10px] font-semibold text-surface-500">Preview (injected into AI context)</p>
        <pre className="text-[10px] text-surface-700 dark:text-surface-300">## Project Rules
{preview || "(no active rules)"}</pre>
      </div>

      <button onClick={save} className="w-full rounded-lg bg-green-600 py-2 text-xs font-medium text-white hover:bg-green-700">
        {saved ? "✅ Saved!" : "Save Rules"}
      </button>
    </div>
  );
}