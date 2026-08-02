import { useState, type FormEvent } from 'react';
import { Workflow as WorkflowIcon, Plus, Play, Loader2, Zap } from 'lucide-react';
import { Modal } from '../components/Modal';
import { useWorkflows, useCreateWorkflow, useExecuteWorkflow } from '../hooks/useWorkflows';
import type { Workflow } from '../types/api';

/** Página de workflows — criação e execução reais via API. */
export function Workflows() {
  const { workflows, isLoading } = useWorkflows();
  const createWorkflow = useCreateWorkflow();
  const executeWorkflow = useExecuteWorkflow();

  const [createOpen, setCreateOpen] = useState(false);
  const [form, setForm] = useState({ name: '', description: '', steps: '1' });
  const [error, setError] = useState<string | null>(null);
  const [executing, setExecuting] = useState<Workflow | null>(null);
  const [execResult, setExecResult] = useState<string | null>(null);
  const [execError, setExecError] = useState<string | null>(null);

  const onCreate = async (e: FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) {
      setError('O nome do workflow é obrigatório.');
      return;
    }
    setError(null);
    const stepsCount = Math.max(1, Math.min(20, parseInt(form.steps, 10) || 1));
    try {
      await createWorkflow.mutateAsync({
        name: form.name.trim(),
        description: form.description.trim() || undefined,
        steps: Array.from({ length: stepsCount }, (_, i) => ({ step: i + 1 })),
      });
      setCreateOpen(false);
      setForm({ name: '', description: '', steps: '1' });
    } catch {
      setError('Não foi possível criar o workflow.');
    }
  };

  const onExecute = async (wf: Workflow) => {
    setExecuting(wf);
    setExecResult(null);
    setExecError(null);
    try {
      const result = await executeWorkflow.mutateAsync({ id: wf.workflow_id });
      setExecResult(
        `Execução ${result.run_id ?? '—'} iniciada (${result.status}). ${JSON.stringify(result.result ?? {})}`
      );
    } catch {
      setExecError('Não foi possível executar o workflow.');
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Workflows</h1>
          <p className="page-subtitle">Crie e execute workflows de automação</p>
        </div>
        <button onClick={() => { setForm({ name: '', description: '', steps: '1' }); setError(null); setCreateOpen(true); }} className="btn-primary">
          <Plus className="h-4 w-4" /> Novo workflow
        </button>
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
      ) : workflows.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <WorkflowIcon className="h-8 w-8 text-ink-muted" />
            <p className="empty-title">Nenhum workflow</p>
            <p className="empty-hint">Crie um workflow para automatizar seus agentes.</p>
            <button onClick={() => { setForm({ name: '', description: '', steps: '1' }); setError(null); setCreateOpen(true); }} className="btn-primary mt-2">
              <Plus className="h-4 w-4" /> Criar workflow
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {workflows.map((wf) => (
            <div key={wf.workflow_id} className="card card-hover flex flex-col p-5">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-50 text-violet-600 dark:bg-violet-500/10 dark:text-violet-400">
                    <WorkflowIcon className="h-5 w-5" />
                  </div>
                  <div className="min-w-0">
                    <p className="truncate font-semibold text-ink">{wf.name}</p>
                    <p className="text-xs text-ink-muted">{wf.steps?.length ?? 0} etapas</p>
                  </div>
                </div>
              </div>

              <p className="mt-3 line-clamp-2 min-h-[2.5rem] flex-1 text-sm text-ink-muted">
                {wf.description || 'Sem descrição.'}
              </p>

              <div className="mt-4 flex items-center justify-between border-t border-line pt-3">
                <div className="flex flex-wrap gap-1.5">
                  {(wf.tags ?? []).slice(0, 3).map((tag) => (
                    <span key={tag} className="badge-neutral">{tag}</span>
                  ))}
                  {(wf.tags ?? []).length === 0 && <span className="text-xs text-ink-muted">Sem tags</span>}
                </div>
                <button
                  onClick={() => void onExecute(wf)}
                  disabled={executeWorkflow.isPending && executing?.workflow_id === wf.workflow_id}
                  className="btn-primary btn-sm"
                >
                  {executeWorkflow.isPending && executing?.workflow_id === wf.workflow_id ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  ) : (
                    <Play className="h-3.5 w-3.5" />
                  )}
                  Executar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal criar workflow */}
      <Modal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        title="Novo workflow"
        description="Defina o nome e a quantidade de etapas."
        footer={
          <>
            <button onClick={() => setCreateOpen(false)} className="btn-secondary" disabled={createWorkflow.isPending}>
              Cancelar
            </button>
            <button type="submit" form="wf-form" className="btn-primary" disabled={createWorkflow.isPending}>
              {createWorkflow.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              Criar workflow
            </button>
          </>
        }
      >
        <form id="wf-form" onSubmit={onCreate} className="space-y-4">
          {error && <p className="text-sm text-danger-600">{error}</p>}
          <label className="block">
            <span className="label">Nome *</span>
            <input
              className="input"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="Pipeline de produção"
            />
          </label>
          <label className="block">
            <span className="label">Descrição</span>
            <textarea
              className="input min-h-20 resize-y"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="O que este workflow automatiza?"
            />
          </label>
          <label className="block">
            <span className="label">Número de etapas (1–20)</span>
            <input
              type="number"
              min={1}
              max={20}
              className="input"
              value={form.steps}
              onChange={(e) => setForm({ ...form, steps: e.target.value })}
            />
          </label>
        </form>
      </Modal>

      {/* Modal resultado de execução */}
      <Modal
        open={Boolean(execResult || execError)}
        onClose={() => { setExecResult(null); setExecError(null); setExecuting(null); }}
        title="Resultado da execução"
        description={`Workflow: ${executing?.name ?? ''}`}
      >
        {execError ? (
          <div className="alert alert-danger">
            <Zap className="h-4 w-4 shrink-0" />
            {execError}
          </div>
        ) : (
          <div className="alert alert-success">
            <Zap className="h-4 w-4 shrink-0" />
            {execResult}
          </div>
        )}
      </Modal>
    </div>
  );
}

export default Workflows;
