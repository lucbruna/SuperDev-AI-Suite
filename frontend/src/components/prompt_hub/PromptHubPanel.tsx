"use client";

import { useState, useEffect } from "react";

export function PromptHubPanel() {
  const [prompts, setPrompts] = useState<any[]>([]);
  const [name, setName] = useState("");
  const [content, setContent] = useState("");
  const [model, setModel] = useState("gpt-4o");
  const [selected, setSelected] = useState<any>(null);
  const [versions, setVersions] = useState<any[]>([]);
  const [diff, setDiff] = useState<any>(null);

  const refresh = async () => {
    try {
      const res = await fetch("/api/prompt-hub/prompts");
      const data = await res.json();
      setPrompts(data.prompts || []);
    } catch {}
  };

  useEffect(() => { refresh(); }, []);

  const create = async () => {
    if (!name.trim() || !content.trim()) return;
    await fetch(`/api/prompt-hub/prompts?name=${encodeURIComponent(name)}&content=${encodeURIComponent(content)}&model=${model}`, { method: "POST" });
    setName(""); setContent(""); setModel("gpt-4o");
    await refresh();
  };

  const selectPrompt = async (p: any) => {
    setSelected(p);
    setDiff(null);
    try {
      const res = await fetch(`/api/prompt-hub/prompts/${p.id}/versions`);
      setVersions((await res.json()).versions || []);
    } catch {}
  };

  const showDiff = async (v1: number, v2: number) => {
    if (!selected) return;
    const res = await fetch(`/api/prompt-hub/prompts/${selected.id}/compare?v1=${v1}&v2=${v2}`);
    setDiff(await res.json());
  };

  return (
    <div className="grid grid-cols-2 gap-4">
      <div className="space-y-4">
        <div className="rounded-xl border p-4 dark:border-surface-700">
          <h3 className="mb-2 text-xs font-semibold text-surface-900 dark:text-surface-50">Create Prompt</h3>
          <div className="space-y-2">
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Prompt name..." className="w-full rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800" />
            <textarea value={content} onChange={(e) => setContent(e.target.value)} placeholder="Prompt content..." rows={6} className="w-full rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs font-mono dark:border-surface-600 dark:bg-surface-800" />
            <select value={model} onChange={(e) => setModel(e.target.value)} className="w-full rounded-lg border border-surface-300 bg-white px-3 py-2 text-xs dark:border-surface-600 dark:bg-surface-800">
              <option value="gpt-4o">GPT-4o</option>
              <option value="gpt-4o-mini">GPT-4o-mini</option>
              <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
              <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
            </select>
            <button onClick={create} disabled={!name.trim() || !content.trim()} className="w-full rounded-lg bg-primary-600 py-2 text-xs font-medium text-white hover:bg-primary-700 disabled:opacity-40">Create</button>
          </div>
        </div>

        {diff && (
          <div className="rounded-xl border p-4 dark:border-surface-700">
            <h3 className="mb-2 text-xs font-semibold text-surface-900 dark:text-surface-50">Diff v{diff.version_a} → v{diff.version_b}</h3>
            <pre className="overflow-x-auto rounded bg-surface-50 p-2 text-[10px] dark:bg-surface-800 dark:text-surface-300">{diff.diff}</pre>
          </div>
        )}
      </div>

      <div className="space-y-4">
        <div className="rounded-xl border dark:border-surface-700">
          <div className="border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
            <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">Prompts ({prompts.length})</span>
          </div>
          <div className="divide-y dark:divide-surface-700">
            {prompts.map((p) => (
              <div key={p.id} onClick={() => selectPrompt(p)} className={`cursor-pointer px-4 py-3 ${selected?.id === p.id ? "bg-primary-50 dark:bg-primary-950" : ""}`}>
                <p className="text-xs font-medium text-surface-900 dark:text-surface-50">{p.name}</p>
                <p className="text-[10px] text-surface-400">v{p.current_version} · {p.model} · {p.tags?.join(", ") || "no tags"}</p>
              </div>
            ))}
          </div>
        </div>

        {selected && versions.length > 0 && (
          <div className="rounded-xl border dark:border-surface-700">
            <div className="border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
              <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">Versions</span>
            </div>
            <div className="divide-y dark:divide-surface-700">
              {versions.map((v: any) => (
                <div key={v.version} className="flex items-center justify-between px-4 py-2">
                  <div>
                    <span className="text-xs font-medium text-surface-700 dark:text-surface-200">v{v.version}</span>
                    <span className="ml-2 text-[10px] text-surface-400">{v.author} · {new Date(v.created_at).toLocaleDateString()}</span>
                  </div>
                  <div className="flex gap-1">
                    <button onClick={() => showDiff(v.version - 1, v.version)} disabled={v.version <= 1} className="rounded bg-surface-100 px-2 py-0.5 text-[9px] dark:bg-surface-700 disabled:opacity-30">Diff</button>
                    <button onClick={async () => { await fetch(`/api/prompt-hub/prompts/${selected.id}/promote?version=${v.version}`, { method: "POST" }); }} className="rounded bg-green-100 px-2 py-0.5 text-[9px] text-green-700 dark:bg-green-900 dark:text-green-300">Promote</button>
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