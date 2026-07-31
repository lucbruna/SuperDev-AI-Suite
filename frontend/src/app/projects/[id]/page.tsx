"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/DashboardLayout";
import { projectsApi } from "@/api/projects";

export default function ProjectDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params?.id;
  const router = useRouter();
  const [project, setProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    projectsApi
      .getProject(id)
      .then(setProject)
      .catch((err) => setError(err?.message || "Erro ao carregar projeto"))
      .finally(() => setLoading(false));
  }, [id]);

  return (
    <DashboardLayout>
      <button onClick={() => router.push("/projects")} className="mb-4 text-sm text-primary-600 hover:underline">
        ← Voltar para Projetos
      </button>

      {loading && <p className="text-surface-400">Carregando...</p>}
      {error && <p className="rounded-lg bg-red-50 p-3 text-sm text-red-600">{error}</p>}

      {project && (
        <div className="rounded-xl border bg-white p-8 shadow-sm dark:border-surface-700 dark:bg-surface-900">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">{project.name}</h1>
              <p className="mt-2 text-surface-600 dark:text-surface-400">
                {project.description || "Sem descrição"}
              </p>
            </div>
            {project.language && (
              <span className="rounded-full bg-primary-100 px-3 py-1 text-sm text-primary-700">
                {project.language}
              </span>
            )}
          </div>

          <div className="mt-6 grid grid-cols-2 gap-4 border-t pt-6 dark:border-surface-700">
            <div>
              <p className="text-sm text-surface-500">Status</p>
              <p className="font-medium text-surface-900 dark:text-surface-50 capitalize">{project.status}</p>
            </div>
            <div>
              <p className="text-sm text-surface-500">Visibilidade</p>
              <p className="font-medium text-surface-900 dark:text-surface-50 capitalize">{project.visibility || "private"}</p>
            </div>
            {project.ownerName && (
              <div>
                <p className="text-sm text-surface-500">Proprietário</p>
                <p className="font-medium text-surface-900 dark:text-surface-50">{project.ownerName}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
