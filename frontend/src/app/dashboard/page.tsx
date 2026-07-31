"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/DashboardLayout";
import { projectsApi } from "@/api/projects";
import { getAgents } from "@/api/agents";
import { llmApi } from "@/api/llm";
import { useAuthStore } from "@/stores/authStore";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface SystemStatus {
  api: "ok" | "error" | "loading";
  llm: "ok" | "error" | "loading";
  llmProviders: number;
}

// ---------------------------------------------------------------------------
// Stat Card
// ---------------------------------------------------------------------------

function StatCard({
  label,
  value,
  icon,
  href,
  color,
}: {
  label: string;
  value: string | number;
  icon: string;
  href: string;
  color: string;
}) {
  return (
    <Link href={href}>
      <div className="rounded-xl border bg-white p-6 shadow-sm transition-all hover:shadow-md dark:border-surface-700 dark:bg-surface-900 cursor-pointer group">
        <div className={`mb-3 inline-flex h-10 w-10 items-center justify-center rounded-lg ${color} text-lg`}>
          {icon}
        </div>
        <p className="text-3xl font-bold text-surface-900 dark:text-surface-50 group-hover:text-primary-600 transition-colors">
          {value}
        </p>
        <p className="mt-1 text-sm text-surface-500">{label}</p>
      </div>
    </Link>
  );
}

// ---------------------------------------------------------------------------
// Quick Action Card
// ---------------------------------------------------------------------------

function QuickAction({
  label,
  description,
  icon,
  href,
  color,
}: {
  label: string;
  description: string;
  icon: string;
  href: string;
  color: string;
}) {
  return (
    <Link href={href}>
      <div className="flex items-center gap-4 rounded-xl border bg-white p-4 shadow-sm transition-all hover:shadow-md hover:border-primary-200 dark:border-surface-700 dark:bg-surface-900 dark:hover:border-primary-800 cursor-pointer group">
        <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl ${color} text-xl`}>
          {icon}
        </div>
        <div className="min-w-0">
          <p className="font-semibold text-surface-900 group-hover:text-primary-600 dark:text-surface-50 transition-colors">
            {label}
          </p>
          <p className="text-sm text-surface-500 truncate">{description}</p>
        </div>
        <span className="ml-auto text-surface-300 group-hover:text-primary-500 transition-colors">
          →
        </span>
      </div>
    </Link>
  );
}

// ---------------------------------------------------------------------------
// Main Dashboard
// ---------------------------------------------------------------------------

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [projectsCount, setProjectsCount] = useState(0);
  const [agentsCount, setAgentsCount] = useState(0);
  const [llmProvidersCount, setLlmProvidersCount] = useState(0);
  const [llmStatus, setLlmStatus] = useState<"ok" | "error" | "loading">("loading");
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);

    const results = await Promise.allSettled([
      projectsApi.getProjects().then((res) => {
        const items = Array.isArray(res) ? res : res?.data || [];
        setProjectsCount(items.length);
      }),
      getAgents().then((data: any) => {
        const items = Array.isArray(data) ? data : [];
        setAgentsCount(items.length);
      }),
      llmApi.listProviders().then((providers) => {
        setLlmProvidersCount(providers.length);
      }),
      llmApi.health().then((health) => {
        setLlmStatus(health.overall === "healthy" ? "ok" : "error");
      }).catch(() => {
        setLlmStatus("error");
      }),
    ]);

    // Even if some fail, we still have partial data
    results.forEach((r) => {
      if (r.status === "fulfilled") return;
    });

    setLoading(false);
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const greeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Bom dia";
    if (hour < 18) return "Boa tarde";
    return "Boa noite";
  };

  return (
    <DashboardLayout>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">
          {greeting()}, {user?.fullName || user?.email?.split("@")[0] || "Dev"}
        </h1>
        <p className="mt-1 text-surface-500">
          Aqui está o resumo do seu SuperDev
        </p>
      </div>

      {/* Stat Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        <StatCard
          label="Projetos"
          value={loading ? "..." : projectsCount}
          icon="📁"
          href="/projects"
          color="bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400"
        />
        <StatCard
          label="Agentes IA"
          value={loading ? "..." : agentsCount}
          icon="🤖"
          href="/agents"
          color="bg-purple-50 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400"
        />
        <StatCard
          label="Chat IA"
          value="→"
          icon="💬"
          href="/chat"
          color="bg-green-50 text-green-600 dark:bg-green-900/30 dark:text-green-400"
        />
        <StatCard
          label="Providers LLM"
          value={loading ? "..." : llmProvidersCount}
          icon="🧠"
          href="/llm/providers"
          color="bg-orange-50 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3 mb-8">
        {/* Quick Actions */}
        <div className="lg:col-span-2">
          <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-surface-50">
            Ações Rápidas
          </h2>
          <div className="space-y-3">
            <QuickAction
              label="Novo Projeto"
              description="Criar um novo projeto no SuperDev"
              icon="➕"
              href="/projects"
              color="bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400"
            />
            <QuickAction
              label="Chat com IA"
              description="Converse com modelos de IA via LLM Chat"
              icon="💬"
              href="/llm/chat"
              color="bg-green-50 text-green-600 dark:bg-green-900/30 dark:text-green-400"
            />
            <QuickAction
              label="Workflows"
              description="Crie e execute workflows automatizados"
              icon="⚡"
              href="/workflows"
              color="bg-yellow-50 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400"
            />
            <QuickAction
              label="Configurações"
              description="Gerencie seu perfil e preferências"
              icon="⚙️"
              href="/settings"
              color="bg-surface-100 text-surface-600 dark:bg-surface-800 dark:text-surface-400"
            />
          </div>
        </div>

        {/* System Status */}
        <div>
          <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-surface-50">
            Status do Sistema
          </h2>
          <div className="rounded-xl border bg-white p-6 shadow-sm dark:border-surface-700 dark:bg-surface-900">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-surface-600 dark:text-surface-400">API Backend</span>
                <span className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-green-500" />
                  <span className="text-sm font-medium text-green-600">Online</span>
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-surface-600 dark:text-surface-400">LLM Providers</span>
                <span className="flex items-center gap-2">
                  <span
                    className={`h-2 w-2 rounded-full ${
                      llmStatus === "loading"
                        ? "bg-yellow-500"
                        : llmStatus === "ok"
                          ? "bg-green-500"
                          : "bg-red-500"
                    }`}
                  />
                  <span
                    className={`text-sm font-medium ${
                      llmStatus === "loading"
                        ? "text-yellow-600"
                        : llmStatus === "ok"
                          ? "text-green-600"
                          : "text-red-600"
                    }`}
                  >
                    {llmStatus === "loading" ? "Verificando..." : llmStatus === "ok" ? "Saudável" : "Erro"}
                  </span>
                </span>
              </div>
              <div className="border-t border-surface-100 pt-4 dark:border-surface-700">
                <p className="text-xs text-surface-400">
                  {llmProvidersCount} provider{llmProvidersCount !== 1 ? "s" : ""} configurado{llmProvidersCount !== 1 ? "s" : ""}
                </p>
              </div>
            </div>
          </div>

          {/* Recent Activity placeholder */}
          <h2 className="mt-6 mb-4 text-lg font-semibold text-surface-900 dark:text-surface-50">
            Atividade Recente
          </h2>
          <div className="rounded-xl border bg-white p-6 shadow-sm dark:border-surface-700 dark:bg-surface-900">
            <p className="text-center text-sm text-surface-400 py-4">
              Nenhuma atividade recente
            </p>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
