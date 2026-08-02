"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/DashboardLayout";
import { settingsApi } from "@/api/settings";
import { useAuthStore } from "@/stores/authStore";

export default function SettingsPage() {
  const { user } = useAuthStore();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (user) {
      setName(user.fullName || "");
      setEmail(user.email || "");
    }
  }, [user]);

  const handleSave = async () => {
    setSaving(true);
    setMessage("");
    try {
      await settingsApi.updateGeneralSettings({ siteName: name } as any);
      setMessage("Configurações salvas!");
    } catch {
      setMessage("Erro ao salvar");
    } finally {
      setSaving(false);
    }
  };

  return (
    <DashboardLayout>
      <h1 className="mb-6 text-2xl font-bold text-surface-900 dark:text-surface-50">Configurações</h1>

      <div className="space-y-6">
        {/* Profile */}
        <div className="rounded-xl border bg-white p-6 shadow-sm dark:border-surface-700 dark:bg-surface-900">
          <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-surface-50">Perfil</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Nome</label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="mt-1 w-full rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Email</label>
              <input
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 w-full rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
                disabled
              />
            </div>
          </div>
          {message && (
            <p className={`mt-3 text-sm ${message.includes("Erro") ? "text-red-500" : "text-green-500"}`}>{message}</p>
          )}
          <button
            onClick={handleSave}
            disabled={saving}
            className="mt-4 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
          >
            {saving ? "Salvando..." : "Salvar Alterações"}
          </button>
        </div>

        {/* Quick Links */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Link
            href="/settings/providers"
            className="rounded-xl border bg-white p-6 shadow-sm transition-all hover:border-primary-300 hover:shadow-md dark:border-surface-700 dark:bg-surface-900"
          >
            <div className="mb-3 text-3xl">🔧</div>
            <h3 className="font-semibold text-surface-900 dark:text-surface-50">Providers de IA</h3>
            <p className="mt-1 text-sm text-surface-500">Configure OpenAI, Anthropic, Google e mais</p>
          </Link>

          <Link
            href="/settings/llm"
            className="rounded-xl border bg-white p-6 shadow-sm transition-all hover:border-primary-300 hover:shadow-md dark:border-surface-700 dark:bg-surface-900"
          >
            <div className="mb-3 text-3xl">🤖</div>
            <h3 className="font-semibold text-surface-900 dark:text-surface-50">Configurações LLM</h3>
            <p className="mt-1 text-sm text-surface-500">Modelo padrão, temperatura, tokens</p>
          </Link>

          <Link
            href="/settings/api-keys"
            className="rounded-xl border bg-white p-6 shadow-sm transition-all hover:border-primary-300 hover:shadow-md dark:border-surface-700 dark:bg-surface-900"
          >
            <div className="mb-3 text-3xl">🔑</div>
            <h3 className="font-semibold text-surface-900 dark:text-surface-50">API Keys</h3>
            <p className="mt-1 text-sm text-surface-500">Gerencie suas chaves de API</p>
          </Link>
        </div>
      </div>
    </DashboardLayout>
  );
}
