"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/DashboardLayout";
import { projectsApi } from "@/api/projects";
import { getAgents } from "@/api/agents";
import { useAuthStore } from "@/stores/authStore";

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState({ projects: 0, agents: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      projectsApi.getProjects().then((r) => setStats((s) => ({ ...s, projects: r.data?.length || 0 }))).catch(() => {}),
      getAgents().then((r) => setStats((s) => ({ ...s, agents: r?.length || 0 }))).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  const cards = [
    { label: "Projetos", value: stats.projects, href: "/projects", color: "bg-blue-500" },
    { label: "Agentes", value: stats.agents, href: "/agents", color: "bg-purple-500" },
  ];

  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">
          Bem-vindo, {user?.fullName || user?.email}
        </h1>
        <p className="mt-1 text-surface-500">Painel de controle do SuperDev</p>
      </div>

      {loading ? (
        <p className="text-surface-400">Carregando...</p>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {cards.map((card) => (
            <Link key={card.label} href={card.href}>
              <div className="rounded-xl border bg-white p-6 shadow-sm transition-shadow hover:shadow-md dark:border-surface-700 dark:bg-surface-900">
                <div className={`mb-3 h-2 w-12 rounded-full ${card.color}`} />
                <p className="text-3xl font-bold text-surface-900 dark:text-surface-50">{card.value}</p>
                <p className="mt-1 text-sm text-surface-500">{card.label}</p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
}
