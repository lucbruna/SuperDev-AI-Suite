"use client";

import React, { FormEvent, useCallback, useEffect, useState } from "react";
import { Card, CardBody, CardHeader } from "@/components/cards/Card";
import { Badge } from "@/components/badges/Badge";
import { Button } from "@/components/buttons/Button";
import {
  workflowsApi,
  type Workflow,
  type WorkflowExecution,
} from "@/api/workflows";

const initialForm = { name: "", description: "", code: "print('Workflow concluído')", tags: "" };

export function WorkflowCanvas() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [executionResult, setExecutionResult] = useState<WorkflowExecution | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState(initialForm);

  const loadWorkflows = useCallback(async () => {
    setError(null);
    try {
      const items = await workflowsApi.list();
      setWorkflows(items);
      setSelectedWorkflow((current) =>
        current ? items.find((item) => item.workflow_id === current.workflow_id) ?? null : null,
      );
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || "Não foi possível carregar os workflows.");
    }
  }, []);

  useEffect(() => {
    loadWorkflows();
  }, [loadWorkflows]);

  const createWorkflow = async (event: FormEvent) => {
    event.preventDefault();
    if (!form.name.trim() || !form.code.trim()) return;
    setIsCreating(true);
    setError(null);
    try {
      const workflow = await workflowsApi.create({
        name: form.name.trim(),
        description: form.description.trim(),
        tags: form.tags.split(",").map((tag) => tag.trim()).filter(Boolean),
        steps: [{
          id: "step-1",
          name: "Executar código",
          step_type: "code",
          config: { language: "python", code: form.code },
        }],
      });
      setWorkflows((current) => [...current, workflow]);
      setSelectedWorkflow(workflow);
      setForm(initialForm);
      setShowCreate(false);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || "Não foi possível criar o workflow.");
    } finally {
      setIsCreating(false);
    }
  };

  const executeWorkflow = async () => {
    if (!selectedWorkflow) return;
    setIsRunning(true);
    setExecutionResult(null);
    setError(null);
    try {
      setExecutionResult(await workflowsApi.execute(selectedWorkflow.workflow_id));
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || "Não foi possível executar o workflow.");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Workflows</h1>
          <p className="mt-1 text-sm text-surface-500">Crie e execute automações conectadas ao backend.</p>
        </div>
        <Button variant="primary" size="sm" onClick={() => setShowCreate(true)}>New Workflow</Button>
      </div>

      {error && <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}

      {showCreate && (
        <Card>
          <CardHeader><h2 className="text-lg font-semibold">Novo workflow</h2></CardHeader>
          <CardBody>
            <form className="space-y-4" onSubmit={createWorkflow}>
              <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Nome" className="w-full rounded-lg border p-2 dark:bg-surface-800" />
              <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Descrição" className="w-full rounded-lg border p-2 dark:bg-surface-800" />
              <textarea required rows={5} value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} placeholder="Código Python a executar" className="w-full rounded-lg border p-2 font-mono text-sm dark:bg-surface-800" />
              <input value={form.tags} onChange={(e) => setForm({ ...form, tags: e.target.value })} placeholder="Tags separadas por vírgula (opcional)" className="w-full rounded-lg border p-2 dark:bg-surface-800" />
              <div className="flex gap-2"><Button type="submit" isLoading={isCreating}>Criar</Button><Button type="button" variant="secondary" onClick={() => setShowCreate(false)}>Cancelar</Button></div>
            </form>
          </CardBody>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Workflows disponíveis</h2>
          {workflows.map((workflow) => (
            <Card key={workflow.workflow_id} className={`cursor-pointer transition-colors ${selectedWorkflow?.workflow_id === workflow.workflow_id ? "border-primary-500" : ""}`} onClick={() => { setSelectedWorkflow(workflow); setExecutionResult(null); }}>
              <CardBody><h3 className="font-medium">{workflow.name}</h3><p className="mt-1 text-sm text-surface-500">{workflow.description || "Sem descrição"}</p><div className="mt-2 flex flex-wrap gap-2"><Badge variant="default">{workflow.steps.length} steps</Badge>{workflow.tags.map((tag) => <Badge key={tag} variant="default" className="text-xs">{tag}</Badge>)}</div></CardBody>
            </Card>
          ))}
          {workflows.length === 0 && <p className="text-sm text-surface-500">Nenhum workflow criado ainda.</p>}
        </div>

        <div className="lg:col-span-2">
          {selectedWorkflow ? <Card><CardHeader><div className="flex items-center justify-between gap-4"><div><h2 className="text-lg font-semibold">{selectedWorkflow.name}</h2><p className="text-sm text-surface-500">{selectedWorkflow.description}</p></div><Button onClick={executeWorkflow} isLoading={isRunning}>{isRunning ? "Executando..." : "Executar"}</Button></div></CardHeader><CardBody><h3 className="font-medium">Etapas</h3>{selectedWorkflow.steps.map((step, index) => <div key={step.id} className="flex items-center gap-3 rounded-lg bg-surface-50 p-3 dark:bg-surface-800"><span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-100 text-sm font-medium text-primary-700">{index + 1}</span><div><p className="font-medium">{step.name}</p><p className="text-sm text-surface-500">{step.step_type}</p></div></div>)}{executionResult && <div className="rounded-lg bg-surface-50 p-4 dark:bg-surface-800"><h4 className="mb-2 font-medium">Resultado: {executionResult.status}</h4><pre className="overflow-auto text-xs whitespace-pre-wrap">{JSON.stringify(executionResult.result, null, 2)}</pre></div>}</CardBody></Card> : <Card className="flex h-64 items-center justify-center"><p className="text-surface-500">Selecione ou crie um workflow.</p></Card>}
        </div>
      </div>
    </div>
  );
}
