import { useState, type FormEvent } from 'react';
import {
  Bot,
  Plus,
  Play,
  Square,
  Trash2,
  Loader2,
  Wrench,
  CheckCircle2,
  XCircle,
  Clock,
} from 'lucide-react';
import { Modal } from '../components/Modal';
import {
  useAgents,
  useCreateAgent,
  useStartAgent,
  useStopAgent,
  useExecuteAgent,
  useDeleteAgent,
} from '../hooks/useAgents';
import type { Agent } from '../types/api';
import { cn } from '../lib/utils';

/** Página de agentes — CRUD, start/stop e execução reais via API. */
export function Agents() {
  const { agents, isLoading } = useAgents();
  const createAgent = useCreateAgent();
  const startAgent = useStartAgent();
  const stopAgent = useStopAgent();
  const executeAgent = useExecuteAgent();
  const deleteAgent = useDeleteAgent();

  const [createOpen, setCreateOpen] = useState(false);
  const [form, setForm] = useState({ name: '', description: '', agent_type: 'general' });
  const [error, setError] = useState<string | null>(null);

  const [executing, setExecuting] = useState<Agent | null>(null);
  const [input, setInput] = useState('');
  const [execResult, setExecResult] = useState<{ output: string; time_ms: number } | null>(null);

  const onCreate = async (e: FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) {
      setError('O nome do agente é obrigatório.');
      return;
    }
    setError(null);
    try {
      await createAgent.mutateAsync({
        name: form.name.trim(),
        description: form.description.trim() || undefined,
        agent_type: form.agent_type,
      });
      setCreateOpen(false);
      setForm({ name: '', description: '', agent_type: 'general' });
    } catch {
      setError('Não foi possível criar o agente.');
    }
  };

  const openExecute = (agent: Agent) => {
    setExecuting(agent);
    setInput('');
    setExecResult(null);
  };

  const onExecute = async (e: FormEvent) => {
    e.preventDefault();
    if (!executing) return;
    setExecResult(null);
    try {
      const result = await executeAgent.mutateAsync({ id: executing.id, input });
      setExecResult({ output: result.output, time_ms: result.execution_time_ms });
    } catch {
      setExecResult({ output: 'Falha na execução do agente.', time_ms: 0 });
    }
  };

  const onDelete = async (agent: Agent) => {
    if (!window.confirm(`Excluir o agente "${agent.name}"?`)) return;
    try {
      await deleteAgent.mutateAsync(agent.id);
    } catch {
      // silencioso
    }
  };

  const toggleRunning = (agent: Agent) => {
    if (agent.status === 'running') {
      void stopAgent.mutateAsync(agent.id);
    } else {
      void startAgent.mutateAsync(agent.id);
    }
  };

  const busy = createAgent.isPending || deleteAgent.isPending;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Agentes</h1>
          <p className="page-subtitle">
            Gerencie os agentes de IA ({agents.length} total,{' '}
            {agents.filter((a) => a.status === 'running').length} ativos)
          </p>
        </div>
        <button
          onClick={() => {
            setForm({ name: '', description: '', agent_type: 'general' });
            setError(null);
            setCreateOpen(true);
          }}
          className="btn-primary"
        >
          <Plus className="h-4 w-4" /> Novo agente
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
      ) : agents.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <Bot className="h-8 w-8 text-ink-muted" />
            <p className="empty-title">Nenhum agente</p>
            <p className="empty-hint">Crie um agente para automatizar tarefas com IA.</p>
            <button
              onClick={() => {
                setForm({ name: '', description: '', agent_type: 'general' });
                setError(null);
                setCreateOpen(true);
              }}
              className="btn-primary mt-2"
            >
              <Plus className="h-4 w-4" /> Criar agente
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {agents.map((agent) => {
            const running = agent.status === 'running';
            return (
              <div key={agent.id} className="card card-hover flex flex-col p-5">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400">
                      <Bot className="h-5 w-5" />
                    </div>
                    <div className="min-w-0">
                      <p className="truncate font-semibold text-ink">{agent.name}</p>
                      <p className="text-xs text-ink-muted">{agent.agent_type}</p>
                    </div>
                  </div>
                  <span className={cn('badge shrink-0', running ? 'badge-active' : 'badge-neutral')}>
                    {running ? (
                      <>
                        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-500" /> ativo
                      </>
                    ) : (
                      agent.status ?? 'parado'
                    )}
                  </span>
                </div>

                <p className="mt-3 line-clamp-2 min-h-[2.5rem] flex-1 text-sm text-ink-muted">
                  {agent.description || 'Sem descrição.'}
                </p>

                <div className="mt-3 flex items-center gap-1.5 text-xs text-ink-muted">
                  <Wrench className="h-3.5 w-3.5" />
                  <span>{agent.tools?.length ?? 0} ferramentas</span>
                </div>

                <div className="mt-4 flex items-center justify-between border-t border-line pt-3">
                  <div className="flex gap-1">
                    <button
                      onClick={() => toggleRunning(agent)}
                      disabled={startAgent.isPending || stopAgent.isPending}
                      className="btn-ghost btn-sm"
                      title={running ? 'Parar agente' : 'Iniciar agente'}
                    >
                      {running ? <Square className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
                      {running ? 'Parar' : 'Iniciar'}
                    </button>
                    <button
                      onClick={() => openExecute(agent)}
                      className="btn-secondary btn-sm"
                      title="Executar agente"
                    >
                      <Clock className="h-3.5 w-3.5" /> Executar
                    </button>
                  </div>
                  <button
                    onClick={() => void onDelete(agent)}
                    className="rounded-lg p-2 text-ink-muted transition hover:bg-danger-50 hover:text-danger-600"
                    aria-label={`Excluir ${agent.name}`}
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Modal criar agente */}
      <Modal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        title="Novo agente"
        description="Configure um novo agente de IA."
        footer={
          <>
            <button onClick={() => setCreateOpen(false)} className="btn-secondary" disabled={busy}>
              Cancelar
            </button>
            <button type="submit" form="agent-form" className="btn-primary" disabled={busy}>
              {busy && <Loader2 className="h-4 w-4 animate-spin" />}
              Criar agente
            </button>
          </>
        }
      >
        <form id="agent-form" onSubmit={onCreate} className="space-y-4">
          {error && <p className="text-sm text-danger-600">{error}</p>}
          <label className="block">
            <span className="label">Nome *</span>
            <input
              className="input"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="Assistente de suporte"
            />
          </label>
          <label className="block">
            <span className="label">Tipo</span>
            <select className="select" value={form.agent_type} onChange={(e) => setForm({ ...form, agent_type: e.target.value })}>
              <option value="general">Geral</option>
              <option value="research">Pesquisa</option>
              <option value="coding">Codificação</option>
              <option value="data_analysis">Análise de dados</option>
            </select>
          </label>
          <label className="block">
            <span className="label">Descrição</span>
            <textarea
              className="input min-h-20 resize-y"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="O que este agente faz?"
            />
          </label>
        </form>
      </Modal>

      {/* Modal executar agente */}
      <Modal
        open={Boolean(executing)}
        onClose={() => { setExecuting(null); setExecResult(null); }}
        title={`Executar · ${executing?.name ?? ''}`}
        description="Envie uma instrução para o agente."
        footer={
          <>
            <button onClick={() => { setExecuting(null); setExecResult(null); }} className="btn-secondary" disabled={executeAgent.isPending}>
              Fechar
            </button>
            <button type="submit" form="exec-form" className="btn-primary" disabled={executeAgent.isPending || !input.trim()}>
              {executeAgent.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              Executar
            </button>
          </>
        }
      >
        <form id="exec-form" onSubmit={onExecute} className="space-y-4">
          <label className="block">
            <span className="label">Instrução</span>
            <textarea
              className="input min-h-24 resize-y"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ex.: Resuma os últimos relatórios..."
              disabled={executeAgent.isPending}
            />
          </label>
          {execResult && (
            <div className={cn('alert', execResult.time_ms === 0 ? 'alert-danger' : 'alert-success')}>
              {execResult.time_ms === 0 ? (
                <XCircle className="h-4 w-4 shrink-0" />
              ) : (
                <CheckCircle2 className="h-4 w-4 shrink-0" />
              )}
              <div className="min-w-0">
                <p className="whitespace-pre-wrap text-sm">{execResult.output}</p>
                {execResult.time_ms > 0 && (
                  <p className="mt-1 text-xs opacity-70">Concluído em {execResult.time_ms} ms</p>
                )}
              </div>
            </div>
          )}
        </form>
      </Modal>
    </div>
  );
}

export default Agents;
