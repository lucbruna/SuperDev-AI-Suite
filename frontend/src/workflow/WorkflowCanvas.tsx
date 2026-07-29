"use client";

import React, { useState, useEffect } from "react";
import { Card, CardHeader, CardBody } from "@/components/cards/Card";
import { Badge } from "@/components/badges/Badge";
import { Button } from "@/components/buttons/Button";

interface WorkflowStep {
  id: string;
  name: string;
  type: string;
  status?: string;
}

interface Workflow {
  id: string;
  name: string;
  description: string;
  steps: WorkflowStep[];
  tags: string[];
}

export function WorkflowCanvas() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [executionResult, setExecutionResult] = useState<any>(null);

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const fetchWorkflows = async () => {
    try {
      const response = await fetch("/api/v1/workflows");
      const data = await response.json();
      // Unwrap {success, data} envelope
      setWorkflows(data.data ?? data);
    } catch (err) {
      console.error("Failed to fetch workflows:", err);
    }
  };

  const executeWorkflow = async () => {
    if (!selectedWorkflow) return;

    setIsRunning(true);
    setExecutionResult(null);

    try {
      const response = await fetch(`/api/v1/workflows/${selectedWorkflow.id}/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      const data = await response.json();
      // Unwrap {success, data} envelope
      setExecutionResult(data.data ?? data);
    } catch (err) {
      setExecutionResult({ error: `${err}` });
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Workflows</h1>
        <Button variant="primary" size="sm">New Workflow</Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Available Workflows</h2>
          {workflows.map((workflow) => (
            <Card
              key={workflow.id}
              className={`cursor-pointer transition-colors ${
                selectedWorkflow?.id === workflow.id ? "border-primary" : ""
              }`}
              onClick={() => setSelectedWorkflow(workflow)}
            >
              <CardBody>
                <h3 className="font-medium">{workflow.name}</h3>
                <p className="text-sm text-muted-foreground mt-1">{workflow.description}</p>
                <div className="flex items-center gap-2 mt-2">
                  <Badge variant="default">{workflow.steps.length} steps</Badge>
                  {workflow.tags.map((tag) => (
                    <Badge key={tag} variant="default" className="text-xs">{tag}</Badge>
                  ))}
                </div>
              </CardBody>
            </Card>
          ))}
        </div>

        <div className="lg:col-span-2">
          {selectedWorkflow ? (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-semibold">{selectedWorkflow.name}</h2>
                    <p className="text-sm text-muted-foreground">{selectedWorkflow.description}</p>
                  </div>
                  <Button
                    onClick={executeWorkflow}
                    disabled={isRunning}
                    variant="primary"
                  >
                    {isRunning ? "Running..." : "Execute"}
                  </Button>
                </div>
              </CardHeader>
              <CardBody>
                <div className="space-y-4">
                  <h3 className="font-medium">Steps</h3>
                  <div className="space-y-2">
                    {selectedWorkflow.steps.map((step, index) => (
                      <div key={step.id} className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg">
                        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-sm font-medium">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <p className="font-medium">{step.name}</p>
                          <p className="text-sm text-muted-foreground">{step.type}</p>
                        </div>
                        {step.status && (
                          <Badge variant={step.status === "completed" ? "success" : step.status === "failed" ? "danger" : "default"}>
                            {step.status}
                          </Badge>
                        )}
                      </div>
                    ))}
                  </div>

                  {executionResult && (
                    <div className="mt-4 p-4 bg-muted/30 rounded-lg">
                      <h4 className="font-medium mb-2">Execution Result</h4>
                      <pre className="text-sm font-mono whitespace-pre-wrap">
                        {JSON.stringify(executionResult, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </CardBody>
            </Card>
          ) : (
            <Card className="h-64 flex items-center justify-center">
              <p className="text-muted-foreground">Select a workflow to view details</p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
