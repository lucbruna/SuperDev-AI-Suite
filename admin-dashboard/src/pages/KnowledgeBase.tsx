import { useState, type FormEvent } from 'react';
import { BookOpen, Plus, Trash2, Search, Loader2, Globe, Lock } from 'lucide-react';
import { Modal } from '../components/Modal';
import {
  useKnowledgeBases,
  useCreateKnowledgeBase,
  useDeleteKnowledgeBase,
  useKnowledgeSearch,
} from '../hooks/useKnowledgeBases';
import type { KnowledgeBase } from '../types/api';
import { formatDate } from '../lib/utils';

/** Página da base de conhecimento — CRUD e busca RAG reais via API. */
export function KnowledgeBase() {
  const { bases, isLoading } = useKnowledgeBases();
  const createKB = useCreateKnowledgeBase();
  const deleteKB = useDeleteKnowledgeBase();
  const searchKB = useKnowledgeSearch();

  const [createOpen, setCreateOpen] = useState(false);
  const [form, setForm] = useState({ name: '', description: '', type: 'documents', is_public: false });
  const [error, setError] = useState<string | null>(null);

  const [searchOpen, setSearchOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Array<Record<string, unknown>>>([]);

  const onCreate = async (e: FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) {
      setError('O nome da base é obrigatório.');
      return;
    }
    setError(null);
    try {
      await createKB.mutateAsync({
        name: form.name.trim(),
        description: form.description.trim() || undefined,
        type: form.type,
        is_public: form.is_public,
      });
      setCreateOpen(false);
      setForm({ name: '', description: '', type: 'documents', is_public: false });
    } catch {
      setError('Não foi possível criar a base de conhecimento.');
    }
  };

  const onSearch = async (e: FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setResults([]);
    try {
      const res = await searchKB.mutateAsync({ query: query.trim() });
      setResults(res.results ?? []);
    } catch {
      setResults([]);
    }
  };

  const onDelete = async (kb: KnowledgeBase) => {
    if (!window.confirm(`Excluir a base "${kb.name}"?`)) return;
    try {
      await deleteKB.mutateAsync(kb.id);
    } catch {
      // silencioso
    }
  };

  const busy = createKB.isPending || deleteKB.isPending;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Base de Conhecimento</h1>
          <p className="page-subtitle">Documentos e fontes para seus agentes ({bases.length} total)</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => { setQuery(''); setResults([]); setSearchOpen(true); }} className="btn-secondary">
            <Search className="h-4 w-4" /> Buscar
          </button>
          <button
            onClick={() => {
              setForm({ name: '', description: '', type: 'documents', is_public: false });
              setError(null);
              setCreateOpen(true);
            }}
            className="btn-primary"
          >
            <Plus className="h-4 w-4" /> Nova base
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="card p-5">
              <div className="skeleton h-4 w-2/3" />
              <div className="skeleton mt-3 h-3 w-1/2" />
            </div>
          ))}
        </div>
      ) : bases.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <BookOpen className="h-8 w-8 text-ink-muted" />
            <p className="empty-title">Nenhuma base de conhecimento</p>
            <p className="empty-hint">Adicione documentos para alimentar seus agentes com RAG.</p>
            <button
              onClick={() => {
                setForm({ name: '', description: '', type: 'documents', is_public: false });
                setError(null);
                setCreateOpen(true);
              }}
              className="btn-primary mt-2"
            >
              <Plus className="h-4 w-4" /> Criar base
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {bases.map((kb) => (
            <div key={kb.id} className="card card-hover flex flex-col p-5">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 text-amber-600 dark:bg-amber-500/10 dark:text-amber-400">
                    <BookOpen className="h-5 w-5" />
                  </div>
                  <div className="min-w-0">
                    <p className="truncate font-semibold text-ink">{kb.name}</p>
                    <p className="text-xs text-ink-muted">{kb.type}</p>
                  </div>
                </div>
                {kb.is_public ? (
                  <span className="badge-info shrink-0">
                    <Globe className="h-3 w-3" /> Público
                  </span>
                ) : (
                  <span className="badge-neutral shrink-0">
                    <Lock className="h-3 w-3" /> Privado
                  </span>
                )}
              </div>

              <p className="mt-3 line-clamp-2 min-h-[2.5rem] flex-1 text-sm text-ink-muted">
                {kb.description || 'Sem descrição.'}
              </p>

              <div className="mt-4 flex items-center justify-between border-t border-line pt-3 text-xs text-ink-muted">
                <span>{kb.created_at ? formatDate(kb.created_at) : '—'}</span>
                <button
                  onClick={() => void onDelete(kb)}
                  className="rounded-lg p-1.5 text-ink-muted transition hover:bg-danger-50 hover:text-danger-600"
                  aria-label={`Excluir ${kb.name}`}
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal criar base */}
      <Modal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        title="Nova base de conhecimento"
        description="Crie uma base para os agentes consultarem."
        footer={
          <>
            <button onClick={() => setCreateOpen(false)} className="btn-secondary" disabled={busy}>
              Cancelar
            </button>
            <button type="submit" form="kb-form" className="btn-primary" disabled={busy}>
              {busy && <Loader2 className="h-4 w-4 animate-spin" />}
              Criar base
            </button>
          </>
        }
      >
        <form id="kb-form" onSubmit={onCreate} className="space-y-4">
          {error && <p className="text-sm text-danger-600">{error}</p>}
          <label className="block">
            <span className="label">Nome *</span>
            <input
              className="input"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="Manuais de produto"
            />
          </label>
          <label className="block">
            <span className="label">Tipo</span>
            <select className="select" value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}>
              <option value="documents">Documentos</option>
              <option value="website">Website</option>
              <option value="notion">Notion</option>
              <option value="github">GitHub</option>
              <option value="slack">Slack</option>
            </select>
          </label>
          <label className="block">
            <span className="label">Descrição</span>
            <textarea
              className="input min-h-20 resize-y"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="O que esta base contém?"
            />
          </label>
          <label className="flex cursor-pointer items-center gap-2 text-sm text-ink">
            <input
              type="checkbox"
              checked={form.is_public}
              onChange={(e) => setForm({ ...form, is_public: e.target.checked })}
              className="h-4 w-4 rounded border-line accent-indigo-600"
            />
            Tornar pública
          </label>
        </form>
      </Modal>

      {/* Modal busca RAG */}
      <Modal
        open={searchOpen}
        onClose={() => setSearchOpen(false)}
        title="Buscar na base de conhecimento"
        description="Busca semântica nos documentos indexados."
        size="lg"
      >
        <form onSubmit={onSearch} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-muted" />
            <input
              className="input pl-10"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ex.: como configurar webhooks?"
              autoFocus
            />
          </div>
          <button type="submit" className="btn-primary" disabled={searchKB.isPending || !query.trim()}>
            {searchKB.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
            Buscar
          </button>
        </form>

        <div className="mt-4 space-y-2">
          {searchKB.isPending ? (
            <div className="space-y-2">
              <div className="skeleton h-16 w-full" />
              <div className="skeleton h-16 w-full" />
            </div>
          ) : results.length === 0 ? (
            <div className="empty-state">
              <Search className="h-6 w-6 text-ink-muted" />
              <p className="empty-title">
                {query.trim() ? 'Nenhum resultado' : 'Digite uma consulta'}
              </p>
              <p className="empty-hint">
                {query.trim()
                  ? 'Nenhum documento corresponde à consulta.'
                  : 'Os resultados da busca aparecerão aqui.'}
              </p>
            </div>
          ) : (
            results.map((r, i) => (
              <div key={i} className="rounded-lg border border-line bg-surface-alt p-4">
                <p className="text-sm font-medium text-ink">
                  {String(r.title ?? r.document_id ?? `Resultado ${i + 1}`)}
                </p>
                <p className="mt-1 line-clamp-3 text-sm text-ink-muted">
                  {String(r.content ?? r.snippet ?? '')}
                </p>
                {typeof r.score === 'number' && (
                  <span className="badge-neutral mt-2">score {(r.score * 100).toFixed(0)}%</span>
                )}
              </div>
            ))
          )}
        </div>
      </Modal>
    </div>
  );
}

export default KnowledgeBase;
