"use client";

import { useState } from "react";
import { DashboardLayout } from "@/components/DashboardLayout";

interface ApiKey {
  id: string;
  name: string;
  key: string;
  createdAt: string;
  lastUsed: string | null;
}

export default function ApiKeysPage() {
  const [keys] = useState<ApiKey[]>([
    { id: "1", name: "Production", key: "sk-••••••••••••a1b2", createdAt: "2026-01-15", lastUsed: "2026-07-28" },
    { id: "2", name: "Development", key: "sk-••••••••••••c3d4", createdAt: "2026-03-20", lastUsed: "2026-07-29" },
  ]);
  const [showNew, setShowNew] = useState(false);
  const [newKeyName, setNewKeyName] = useState("");

  const handleGenerate = () => {
    setShowNew(false);
    setNewKeyName("");
  };

  return (
    <DashboardLayout>
      <div className="space-y-6 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-surface-900 dark:text-white">API Keys</h1>
            <p className="text-surface-500">Gerencie suas chaves de API</p>
          </div>
          <button onClick={() => setShowNew(true)} className="rounded-lg bg-primary-600 px-4 py-2 text-white hover:bg-primary-700">
            + Nova Key
          </button>
        </div>

        {showNew && (
          <div className="rounded-lg border bg-surface-50 p-4 dark:border-surface-700 dark:bg-surface-800/50">
            <label className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">Nome da key</label>
            <div className="flex gap-2">
              <input type="text" value={newKeyName} onChange={(e) => setNewKeyName(e.target.value)}
                className="flex-1 rounded-lg border px-4 py-2 dark:border-surface-600 dark:bg-surface-800"
                placeholder="Ex: Produção" />
              <button onClick={handleGenerate} disabled={!newKeyName}
                className="rounded-lg bg-primary-600 px-4 py-2 text-white hover:bg-primary-700 disabled:opacity-50">
                Gerar
              </button>
              <button onClick={() => setShowNew(false)} className="rounded-lg border px-4 py-2 dark:border-surface-600">
                Cancelar
              </button>
            </div>
          </div>
        )}

        <div className="rounded-lg border dark:border-surface-700">
          <table className="w-full">
            <thead>
              <tr className="border-b dark:border-surface-700 text-left text-sm text-surface-500">
                <th className="p-4">Nome</th>
                <th className="p-4">Chave</th>
                <th className="p-4">Criada em</th>
                <th className="p-4">Último uso</th>
                <th className="p-4"></th>
              </tr>
            </thead>
            <tbody>
              {keys.map((k) => (
                <tr key={k.id} className="border-b dark:border-surface-700">
                  <td className="p-4 font-medium">{k.name}</td>
                  <td className="p-4 font-mono text-sm">{k.key}</td>
                  <td className="p-4 text-sm text-surface-500">{k.createdAt}</td>
                  <td className="p-4 text-sm text-surface-500">{k.lastUsed || "—"}</td>
                  <td className="p-4">
                    <button className="text-sm text-red-600 hover:underline">Remover</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </DashboardLayout>
  );
}
