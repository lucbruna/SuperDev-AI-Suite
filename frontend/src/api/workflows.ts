import apiClient from "@/api/client";

export interface WorkflowStep {
  id: string;
  name: string;
  step_type: string;
  config: Record<string, unknown>;
  depends_on?: string[];
}

export interface Workflow {
  workflow_id: string;
  name: string;
  description: string;
  steps: WorkflowStep[];
  tags: string[];
}

export interface CreateWorkflowInput {
  name: string;
  description?: string;
  steps: WorkflowStep[];
  tags?: string[];
}

export interface WorkflowExecution {
  run_id: string;
  workflow_id: string;
  status: string;
  result: Record<string, unknown>;
}

export const workflowsApi = {
  async list(): Promise<Workflow[]> {
    const { data } = await apiClient.get<Workflow[]>("/workflows");
    return data;
  },

  async create(input: CreateWorkflowInput): Promise<Workflow> {
    const { data } = await apiClient.post<Workflow>("/workflows", input);
    return data;
  },

  async execute(workflowId: string): Promise<WorkflowExecution> {
    const { data } = await apiClient.post<WorkflowExecution>(
      `/workflows/${workflowId}/execute`,
      { variables: {} },
    );
    return data;
  },
};
