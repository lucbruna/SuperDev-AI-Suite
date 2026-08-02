"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/DashboardLayout";
import apiClient from "@/api/client";

interface ProjectSettings {
  id: string;
  name: string;
  description: string;
  visibility: string;
  created_at: string;
  updated_at: string;
}

export default function ProjectSettingsPage() {
  const params = useParams<{ id: string }>() ?? { id: "" };
  const router = useRouter();
  const projectId = params.id as string;
  const [settings, setSettings] = useState<ProjectSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchSettings();
  }, [projectId]);

  const fetchSettings = async () => {
    setLoading(true);
    setMessage("");
    try {
      const { data } = await apiClient.get(`/projects/${projectId}`);
      setSettings({
        id: data.id || projectId,
        name: data.name || "",
        description: data.description || "",
        visibility: data.visibility || "private",
        created_at: data.created_at || "",
        updated_at: data.updated_at || "",
      });
    } catch (err: any) {
      setMessage("Erro ao carregar configurações do projeto");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!settings) return;
    setSaving(true);
    setMessage("");
    try {
      const { data } = await apiClient.put(`/projects/${projectId}`, {
        name: settings.name,
        description: settings.description,
      });
      setSettings({
        id: data.id || settings.id,
        name: data.name || settings.name,
        description: data.description || "",
        visibility: data.visibility || settings.visibility,
        created_at: data.created_at || settings.created_at,
        updated_at: data.updated_at || settings.updated_at,
      });
      setMessage("Configurações salvas com sucesso!");
    } catch (err: any) {
      setMessage("Erro ao salvar configurações");
    } finally {
      setSaving(false);
    }
  };

  const formatDate = (value: string) => {
    if (!value) return "—";
    const date = new Date(value);
    return isNaN(date.getTime()) ? value : date.toLocaleString();
  };

  if (loading) {
    return (
      <DashboardLayout>
        <p className="text-surface-400">Carregando...</p>
      </DashboardLayout>
    );
  }

  if (!settings) {
    return (
      <DashboardLayout>
        <p className="text-red-500">Projeto não encontrado</p>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">Configurações do Projeto</h1>
          <p className="mt-1 text-sm text-surface-500">{settings.name}</p>
        </div>
        <button
          onClick={() => router.push(`/projects/${projectId}`)}
          className="rounded-lg border px-4 py-2 text-sm font-medium text-surface-600 hover:bg-surface-50 dark:border-surface-600"
        >
          ← Voltar ao Projeto
        </button>
      </div>

      {message && (
        <div className={`mb-4 rounded-lg p-3 text-sm ${message.includes("Erro") ? "bg-red-50 text-red-600" : "bg-green-50 text-green-600"}`}>
          {message}
          <button onClick={() => setMessage("")} className="ml-2 text-surface-400 hover:text-surface-600">×</button>
        </div>
      )}

      <div className="space-y-6">
        {/* General */}
        <div className="rounded-xl border bg-white p-6 shadow-sm dark:border-surface-700 dark:bg-surface-900">
          <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-surface-50">Geral</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Nome</label>
              <input
                value={settings.name}
                onChange={(e) => setSettings({ ...settings, name: e.target.value })}
                className="mt-1 w-full rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Descrição</label>
              <textarea
                value={settings.description}
                onChange={(e) => setSettings({ ...settings, description: e.target.value })}
                rows={3}
                className="mt-1 w-full rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
              />
            </div>
          </div>
        </div>

        {/* Metadata (read-only) */}
        <div className="rounded-xl border bg-white p-6 shadow-sm dark:border-surface-700 dark:bg-surface-900">
          <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-surface-50">Metadados</h2>
          <dl className="space-y-3 text-sm">
            <div className="flex items-center justify-between">
              <dt className="text-surface-500">ID</dt>
              <dd className="font-mono text-surface-900 dark:text-surface-50">{settings.id}</dd>
            </div>
            <div className="flex items-center justify-between">
              <dt className="text-surface-500">Visibilidade</dt>
              <dd className="capitalize text-surface-900 dark:text-surface-50">{settings.visibility}</dd>
            </div>
            <div className="flex items-center justify-between">
              <dt className="text-surface-500">Criado em</dt>
              <dd className="text-surface-900 dark:text-surface-50">{formatDate(settings.created_at)}</dd>
            </div>
            <div className="flex items-center justify-between">
              <dt className="text-surface-500">Atualizado em</dt>
              <dd className="text-surface-900 dark:text-surface-50">{formatDate(settings.updated_at)}</dd>
            </div>
          </dl>
        </div>

        <button
          onClick={handleSave}
          disabled={saving || !settings.name.trim()}
          className="rounded-lg bg-primary-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
        >
          {saving ? "Salvando..." : "Salvar Configurações"}
        </button>
      </div>
    </DashboardLayout>
  );
}
