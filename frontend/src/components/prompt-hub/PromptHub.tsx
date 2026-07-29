"use client";

import { useState, useEffect } from "react";
import { api } from "@/utils/api-fetch";

interface Prompt {
  id: string;
  name: string;
  description: string;
  current_version: number;
  model: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

interface Version {
  version: number;
  content: string;
  created_at: string;
  author: string;
}

export function PromptHub() {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [selected, setSelected] = useState<Prompt | null>(null);
  const [versions, setVersions] = useState<Version[]>([]);
  const [diff, setDiff] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [content, setContent] = useState("");
  const [model, setModel] = useState("gpt-4o");
  const [tags, setTags] = useState("");
  const [showCreate, setShowCreate] = useState(false);

  useEffect(() => {
    api.get<any>("/api/prompt-hub/prompts").then((d) => setPrompts(d.prompts || [])).catch(() => {});
  }, []);

  const select = async (p: Prompt) => {
    setSelected(p);
    setName(p.name);
    setModel(p.model);
    setTags(p.tags.join(", "));
    const data = await api.get<any>(`/api/prompt-hub/prompts/${p.id}`);
    setVersions(data.versions || []);
    setContent(data.versions?.[data.versions.length - 1]?.content || "");
    setDiff(null);
  };

  const create = async () => {
    const data = await api.post<any>(`/api/prompt-hub/prompts?name=${encodeURIComponent(name)}&content=${encodeURIComponent(content)}&model=${model}&tags=${encodeURIComponent(tags)}`);
    setPrompts((prev) => [...prev, data]);
    setShowCreate(false);
  };

  const saveVersion = async () => {
    if (!selected) return;
    const data = await api.put<any>(`/api/prompt-hub/prompts/${selected.id}`, { content });
    if (data.status === "updated") {
      select(selected);
    }
  };

  const showDiff = async (v1: number, v2: number) => {
    if (!selected) return;
    const data = await api.get<any>(`/api/prompt-hub/prompts/${selected.id}/diff?v1=${v1}&v2=${v2}`);
    setDiff(data.diff);
  };

  return (
    <div className="grid grid-cols-3 gap-4">
      <div className="rounded-xl border dark:border-surface-700">
        <div className="flex items-center justify-between border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
          <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">Prompts ({prompts.length})</span>
          <button onClick={() => setShowCreate(!showCreate)} className="rounded bg-primary-600 px-2 py-1 text-[10px] text-white hover:bg-primary-700">+ New</button>
        </div>
        <div className="space-y-1 p-2">
          {showCreate && (
            <div className="rounded-lg border bg-surface-50 p-2 dark:bg-surface-800">
              <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Prompt name" className="mb-1 w-full rounded border bg-white px-2 py-1 text-xs dark:border-surface-600 dark:bg-surface-700" />
              <textarea value={content} onChange={(e) => setContent(e.target.value)} rows={4} placeholder="Prompt content" className="mb-1 w-full rounded border bg-white px-2 py-1 text-xs font-mono dark:border-surface-600 dark:bg-surface-700" />
              <div className="flex gap-1">
                <input value={model} onChange={(e) => setModel(e.target.value)} className="w-20 rounded border bg-white px-2 py-1 text-[10px] dark:border-surface-600 dark:bg-surface-700" />
                <input value={tags} onChange={(e) => setTags(e.target.value)} placeholder="tags" className="flex-1 rounded border bg-white px-2 py-1 text-[10px] dark:border-surface-600 dark:bg-surface-700" />
                <button onClick={create} className="rounded bg-primary-600 px-2 py-1 text-[10px] text-white">Save</button>
              </div>
            </div>
          )}
          {prompts.map((p) => (
            <button key={p.id} onClick={() => select(p)} className={`w-full rounded-lg px-3 py-2 text-left hover:bg-surface-50 dark:hover:bg-surface-800 ${selected?.id === p.id ? "bg-primary-50 dark:bg-primary-900/20" : ""}`}>
              <p className="text-xs font-medium text-surface-900 dark:text-surface-50">{p.name}</p>
              <p className="text-[10px] text-surface-500">v{p.current_version} · {p.model} · {p.tags.join(", ")}</p>
            </button>
          ))}
        </div>
      </div>

      <div className="col-span-2 rounded-xl border dark:border-surface-700">
        {selected ? (
          <>
            <div className="flex items-center justify-between border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
              <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">{selected.name} — v{selected.current_version}</span>
              <button onClick={saveVersion} className="rounded bg-primary-600 px-2 py-1 text-[10px] text-white hover:bg-primary-700">Save New Version</button>
            </div>
            <textarea value={content} onChange={(e) => setContent(e.target.value)} rows={12} className="w-full border-0 bg-white p-4 text-xs font-mono outline-none dark:bg-surface-900 dark:text-surface-100" />
            <div className="border-t bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
              <span className="text-[10px] font-medium text-surface-500">Version history</span>
              <div className="mt-1 flex flex-wrap gap-1">
                {versions.map((v, i) => (
                  <div key={v.version} className="flex items-center gap-1">
                    <span className={`rounded px-1.5 py-0.5 text-[9px] ${v.version === selected.current_version ? "bg-primary-100 text-primary-700" : "bg-surface-200 text-surface-600 dark:bg-surface-700"}`}>v{v.version}</span>
                    {i < versions.length - 1 && (
                      <button onClick={() => showDiff(v.version, versions[i + 1].version)} className="text-[9px] text-primary-500 hover:text-primary-700">diff</button>
                    )}
                  </div>
                ))}
              </div>
              {diff && (
                <pre className="mt-2 max-h-32 overflow-y-auto rounded bg-black p-2 text-[9px] text-green-400 font-mono">{diff.slice(0, 2000)}</pre>
              )}
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center p-8 text-xs text-surface-400">Select or create a prompt to edit</div>
        )}
      </div>
    </div>
  );
}