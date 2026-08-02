import { useState, type FormEvent } from 'react';
import { Building2, Plus, Pencil, Trash2, Users, Loader2 } from 'lucide-react';
import { Modal } from '../components/Modal';
import {
  useOrganizations,
  useCreateOrganization,
  useUpdateOrganization,
  useDeleteOrganization,
  useOrganizationMembers,
} from '../hooks/useOrganizations';
import type { Organization } from '../types/api';
import { formatDate } from '../lib/utils';
import { cn } from '../lib/utils';

const PLAN_BADGE: Record<string, string> = {
  free: 'badge-neutral',
  pro: 'badge-info',
  enterprise: 'badge-warning',
};

/** Página de organizações — CRUD real via API. */
export function Organizations() {
  const { organizations, total, isLoading } = useOrganizations();
  const createOrg = useCreateOrganization();
  const updateOrg = useUpdateOrganization();
  const deleteOrg = useDeleteOrganization();

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Organization | null>(null);
  const [membersOf, setMembersOf] = useState<Organization | null>(null);
  const [form, setForm] = useState({ name: '', slug: '', description: '', plan: 'free' });
  const [error, setError] = useState<string | null>(null);

  const openCreate = () => {
    setEditing(null);
    setForm({ name: '', slug: '', description: '', plan: 'free' });
    setError(null);
    setModalOpen(true);
  };

  const openEdit = (org: Organization) => {
    setEditing(org);
    setForm({
      name: org.name,
      slug: org.slug,
      description: org.description ?? '',
      plan: org.plan ?? 'free',
    });
    setError(null);
    setModalOpen(true);
  };

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!form.name.trim() || !form.slug.trim()) {
      setError('Nome e slug são obrigatórios.');
      return;
    }
    setError(null);
    try {
      if (editing) {
        await updateOrg.mutateAsync({
          id: editing.id,
          data: { name: form.name.trim(), slug: form.slug.trim(), description: form.description.trim() || null, plan: form.plan },
        });
      } else {
        await createOrg.mutateAsync({
          name: form.name.trim(),
          slug: form.slug.trim().toLowerCase().replace(/\s+/g, '-'),
          description: form.description.trim() || undefined,
          plan: form.plan,
        });
      }
      setModalOpen(false);
    } catch {
      setError('Não foi possível salvar a organização.');
    }
  };

  const onDelete = async (org: Organization) => {
    if (!window.confirm(`Excluir a organização "${org.name}"?`)) return;
    try {
      await deleteOrg.mutateAsync(org.id);
    } catch {
      // erro tratado pelo fallback silencioso da mutation
    }
  };

  const { members } = useOrganizationMembers(membersOf?.id);
  const busy = createOrg.isPending || updateOrg.isPending || deleteOrg.isPending;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Organizações</h1>
          <p className="page-subtitle">
            Gerencie as organizações do SuperDev ({total} total)
          </p>
        </div>
        <button onClick={openCreate} className="btn-primary">
          <Plus className="h-4 w-4" /> Nova organização
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
      ) : organizations.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <Building2 className="h-8 w-8 text-ink-muted" />
            <p className="empty-title">Nenhuma organização</p>
            <p className="empty-hint">Crie a primeira organização para começar.</p>
            <button onClick={openCreate} className="btn-primary mt-2">
              <Plus className="h-4 w-4" /> Criar organização
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {organizations.map((org) => (
            <div key={org.id} className="card card-hover flex flex-col p-5">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 dark:bg-indigo-500/10 dark:text-indigo-400">
                    <Building2 className="h-5 w-5" />
                  </div>
                  <div className="min-w-0">
                    <p className="truncate font-semibold text-ink">{org.name}</p>
                    <p className="text-xs text-ink-muted">/{org.slug}</p>
                  </div>
                </div>
                <span className={cn('badge shrink-0', PLAN_BADGE[org.plan ?? 'free'] ?? 'badge-neutral')}>
                  {org.plan ?? 'free'}
                </span>
              </div>

              <p className="mt-3 line-clamp-2 min-h-[2.5rem] text-sm text-ink-muted">
                {org.description || 'Sem descrição.'}
              </p>

              <div className="mt-4 flex items-center gap-4 border-t border-line pt-3 text-xs text-ink-muted">
                <button
                  onClick={() => setMembersOf(org)}
                  className="flex items-center gap-1.5 transition hover:text-ink"
                >
                  <Users className="h-3.5 w-3.5" /> {org.memberCount ?? 0} membros
                </button>
                <span>{org.createdAt ? formatDate(org.createdAt) : '—'}</span>
                <div className="ml-auto flex gap-1">
                  <button
                    onClick={() => openEdit(org)}
                    className="rounded-lg p-1.5 text-ink-muted transition hover:bg-surface-alt hover:text-ink"
                    aria-label={`Editar ${org.name}`}
                  >
                    <Pencil className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => void onDelete(org)}
                    className="rounded-lg p-1.5 text-ink-muted transition hover:bg-danger-50 hover:text-danger-600"
                    aria-label={`Excluir ${org.name}`}
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal criar/editar */}
      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editing ? 'Editar organização' : 'Nova organização'}
        description={editing ? `Atualize os dados de ${editing.name}.` : 'Preencha os dados para criar uma organização.'}
        footer={
          <>
            <button onClick={() => setModalOpen(false)} className="btn-secondary" disabled={busy}>
              Cancelar
            </button>
            <button type="submit" form="org-form" className="btn-primary" disabled={busy}>
              {busy && <Loader2 className="h-4 w-4 animate-spin" />}
              {editing ? 'Salvar alterações' : 'Criar organização'}
            </button>
          </>
        }
      >
        <form id="org-form" onSubmit={onSubmit} className="space-y-4">
          {error && <p className="text-sm text-danger-600">{error}</p>}
          <label className="block">
            <span className="label">Nome *</span>
            <input
              className="input"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="Acme Inc."
            />
          </label>
          <label className="block">
            <span className="label">Slug *</span>
            <input
              className="input"
              value={form.slug}
              onChange={(e) => setForm({ ...form, slug: e.target.value })}
              placeholder="acme-inc"
              disabled={Boolean(editing)}
            />
          </label>
          <label className="block">
            <span className="label">Descrição</span>
            <textarea
              className="input min-h-20 resize-y"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="Breve descrição da organização"
            />
          </label>
          <label className="block">
            <span className="label">Plano</span>
            <select className="select" value={form.plan} onChange={(e) => setForm({ ...form, plan: e.target.value })}>
              <option value="free">Free</option>
              <option value="pro">Pro</option>
              <option value="enterprise">Enterprise</option>
            </select>
          </label>
        </form>
      </Modal>

      {/* Modal membros */}
      <Modal
        open={Boolean(membersOf)}
        onClose={() => setMembersOf(null)}
        title={`Membros · ${membersOf?.name ?? ''}`}
        description="Membros vinculados a esta organização."
      >
        {members.length === 0 ? (
          <div className="empty-state">
            <Users className="h-6 w-6 text-ink-muted" />
            <p className="empty-title">Sem membros</p>
            <p className="empty-hint">Convide usuários para esta organização.</p>
          </div>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Usuário</th>
                  <th>Função</th>
                </tr>
              </thead>
              <tbody>
                {members.map((m) => (
                  <tr key={m.id}>
                    <td className="font-medium text-ink">
                      {m.user?.full_name || m.user?.email || m.user_id}
                    </td>
                    <td>
                      <span className={m.role === 'owner' ? 'badge-warning' : 'badge-neutral'}>{m.role}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Modal>
    </div>
  );
}

export default Organizations;
