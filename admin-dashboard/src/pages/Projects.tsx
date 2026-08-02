import { useState, type FormEvent } from 'react';
import { FolderKanban, Plus, Pencil, Trash2, Globe, Lock, Loader2 } from 'lucide-react';
import { Modal } from '../components/Modal';
import { useProjects, useCreateProject, useUpdateProject, useDeleteProject } from '../hooks/useProjects';
import type { Project } from '../types/api';
import { formatDate } from '../lib/utils';

/** Página de projetos — CRUD real via API. */
export function Projects() {
  const { projects, total, isLoading } = useProjects();
  const createProject = useCreateProject();
  const updateProject = useUpdateProject();
  const deleteProject = useDeleteProject();

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Project | null>(null);
  const [form, setForm] = useState({ name: '', description: '' });
  const [error, setError] = useState<string | null>(null);

  const openCreate = () => {
    setEditing(null);
    setForm({ name: '', description: '' });
    setError(null);
    setModalOpen(true);
  };

  const openEdit = (p: Project) => {
    setEditing(p);
    setForm({ name: p.name, description: p.description ?? '' });
    setError(null);
    setModalOpen(true);
  };

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) {
      setError('O nome do projeto é obrigatório.');
      return;
    }
    setError(null);
    try {
      if (editing) {
        await updateProject.mutateAsync({ id: editing.id, data: { name: form.name.trim(), description: form.description.trim() } });
      } else {
        await createProject.mutateAsync({ name: form.name.trim(), description: form.description.trim() || undefined });
      }
      setModalOpen(false);
    } catch {
      setError('Não foi possível salvar o projeto.');
    }
  };

  const onDelete = async (p: Project) => {
    if (!window.confirm(`Excluir o projeto "${p.name}"?`)) return;
    try {
      await deleteProject.mutateAsync(p.id);
    } catch {
      // erro tratado silenciosamente
    }
  };

  const busy = createProject.isPending || updateProject.isPending || deleteProject.isPending;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Projetos</h1>
          <p className="page-subtitle">Gerencie os projetos do SuperDev ({total} total)</p>
        </div>
        <button onClick={openCreate} className="btn-primary">
          <Plus className="h-4 w-4" /> Novo projeto
        </button>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="card p-5">
              <div className="skeleton h-4 w-2/3" />
              <div className="skeleton mt-3 h-3 w-1/2" />
              <div className="skeleton mt-3 h-3 w-1/3" />
            </div>
          ))}
        </div>
      ) : projects.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <FolderKanban className="h-8 w-8 text-ink-muted" />
            <p className="empty-title">Nenhum projeto</p>
            <p className="empty-hint">Crie o primeiro projeto para começar.</p>
            <button onClick={openCreate} className="btn-primary mt-2">
              <Plus className="h-4 w-4" /> Criar projeto
            </button>
          </div>
        </div>
      ) : (
        <div className="card">
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Projeto</th>
                  <th>Visibilidade</th>
                  <th>Criado em</th>
                  <th>Atualizado</th>
                  <th className="text-right">Ações</th>
                </tr>
              </thead>
              <tbody>
                {projects.map((p) => (
                  <tr key={p.id}>
                    <td>
                      <div className="flex items-center gap-3">
                        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-sky-50 text-sky-600 dark:bg-sky-500/10 dark:text-sky-400">
                          <FolderKanban className="h-4 w-4" />
                        </div>
                        <div className="min-w-0">
                          <p className="truncate font-medium text-ink">{p.name}</p>
                          {p.description && (
                            <p className="max-w-md truncate text-xs text-ink-muted">{p.description}</p>
                          )}
                        </div>
                      </div>
                    </td>
                    <td>
                      {p.visibility === 'public' ? (
                        <span className="badge-info">
                          <Globe className="h-3 w-3" /> Público
                        </span>
                      ) : (
                        <span className="badge-neutral">
                          <Lock className="h-3 w-3" /> Privado
                        </span>
                      )}
                    </td>
                    <td className="text-ink-muted">{p.created_at ? formatDate(p.created_at) : '—'}</td>
                    <td className="text-ink-muted">{p.updated_at ? formatDate(p.updated_at) : '—'}</td>
                    <td className="text-right">
                      <div className="flex justify-end gap-1">
                        <button
                          onClick={() => openEdit(p)}
                          className="rounded-lg p-1.5 text-ink-muted transition hover:bg-surface-alt hover:text-ink"
                          aria-label={`Editar ${p.name}`}
                        >
                          <Pencil className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => void onDelete(p)}
                          className="rounded-lg p-1.5 text-ink-muted transition hover:bg-danger-50 hover:text-danger-600"
                          aria-label={`Excluir ${p.name}`}
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editing ? 'Editar projeto' : 'Novo projeto'}
        description={editing ? `Atualize os dados de ${editing.name}.` : 'Preencha os dados para criar um projeto.'}
        footer={
          <>
            <button onClick={() => setModalOpen(false)} className="btn-secondary" disabled={busy}>
              Cancelar
            </button>
            <button type="submit" form="project-form" className="btn-primary" disabled={busy}>
              {busy && <Loader2 className="h-4 w-4 animate-spin" />}
              {editing ? 'Salvar alterações' : 'Criar projeto'}
            </button>
          </>
        }
      >
        <form id="project-form" onSubmit={onSubmit} className="space-y-4">
          {error && <p className="text-sm text-danger-600">{error}</p>}
          <label className="block">
            <span className="label">Nome *</span>
            <input
              className="input"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="Meu projeto"
            />
          </label>
          <label className="block">
            <span className="label">Descrição</span>
            <textarea
              className="input min-h-20 resize-y"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="Breve descrição do projeto"
            />
          </label>
        </form>
      </Modal>
    </div>
  );
}

export default Projects;
