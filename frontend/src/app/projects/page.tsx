"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/DashboardLayout";
import { projectsApi } from "@/api/projects";

interface ProjectItem {
  id: string;
  name: string;
  description: string;
  status: string;
  language?: string;
}

export default function ProjectsPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<ProjectItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    projectsApi
      .getProjects()
      .then((res) => {
        const items = Array.isArray(res) ? res : res.data || [];
        setProjects(items);
      })
      .catch((err) => setError(err?.message || "Erro ao carregar projetos"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <DashboardLayout>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">Projetos</h1>
          <p className="mt-1 text-sm text-surface-500">Gerencie seus projetos</p>
        </div>
        <button
          onClick={() => router.push("/projects/new")}
          className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
        >
          + Novo Projeto
        </button>
      </div>

      {loading && <p className="text-surface-400">Carregando...</p>}
      {error && <p className="rounded-lg bg-red-50 p-3 text-sm text-red-600">{error}</p>}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {projects.map((project) => (
          <div
            key={project.id}
            className="rounded-xl border bg-white p-6 shadow-sm dark:border-surface-700 dark:bg-surface-900"
          >
            <div className="flex items-start justify-between">
              <h3 className="font-semibold text-surface-900 dark:text-surface-50">{project.name}</h3>
              <span
                className={`rounded-full px-2 py-1 text-xs font-medium ${
                  project.status === "active"
                    ? "bg-green-100 text-green-700"
                    : "bg-yellow-100 text-yellow-700"
                }`}
              >
                {project.status}
              </span>
            </div>
            <p className="mt-2 text-sm text-surface-500">{project.description || "Sem descrição"}</p>
            {project.language && (
              <span className="mt-2 inline-block rounded bg-surface-100 px-2 py-0.5 text-xs text-surface-600">
                {project.language}
              </span>
            )}
            <button
              onClick={() => router.push(`/projects/${project.id}`)}
              className="mt-4 text-sm font-medium text-primary-600 hover:underline"
            >
              Abrir →
            </button>
          </div>
        ))}
        {!loading && projects.length === 0 && (
          <p className="col-span-full text-center text-surface-400">Nenhum projeto encontrado.</p>
        )}
      </div>
    </DashboardLayout>
  );
}
