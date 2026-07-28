"use client";

const TEMPLATES = [
  {
    name: "CI Pipeline",
    description: "Build, test, and deploy on every push",
    yaml: `name: ci-pipeline
version: "1.0"
steps:
  - type: code
    language: python
    command: "pip install -r requirements.txt && pytest"
  - type: code
    language: node
    command: "npm ci && npm run build"
  - type: deploy
    environment: staging
    strategy: blue-green`,
  },
  {
    name: "Agent Trio",
    description: "Architect → Coder → Reviewer pipeline",
    yaml: `name: agent-trio
version: "1.0"
steps:
  - type: agent
    agent: Architect
    prompt: "Design the solution"
    model: gpt-4o
  - type: agent
    agent: Coder
    prompt: "Implement the solution"
    model: claude-3
  - type: agent
    agent: Reviewer
    prompt: "Review the implementation"
    model: gemini-1.5`,
  },
  {
    name: "Infra Provision",
    description: "Provision cloud resources via Terraform",
    yaml: `name: infra-provision
version: "1.0"
steps:
  - type: code
    language: hcl
    command: "terraform init && terraform plan"
  - type: deploy
    environment: production
    strategy: rolling
  - type: notification
    channel: slack
    message: "Infrastructure provisioned"`,
  },
  {
    name: "Data Pipeline",
    description: "Extract, transform, and load data",
    yaml: `name: data-pipeline
version: "1.0"
steps:
  - type: agent
    agent: DataExtractor
    prompt: "Extract data from source"
    model: gpt-4o
  - type: code
    language: python
    command: "python transform.py"
  - type: code
    language: python
    command: "python load.py --target warehouse"`,
  },
];

interface TemplatesProps {
  onSelect: (yaml: string) => void;
}

export function Templates({ onSelect }: TemplatesProps) {
  return (
    <div className="rounded-xl border dark:border-surface-700">
      <div className="border-b bg-surface-50 px-4 py-2 dark:border-surface-700 dark:bg-surface-800">
        <span className="text-xs font-semibold text-surface-600 dark:text-surface-300">Templates</span>
      </div>
      <div className="grid grid-cols-2 gap-2 p-3">
        {TEMPLATES.map((t) => (
          <button
            key={t.name}
            onClick={() => onSelect(t.yaml)}
            className="rounded-lg border bg-white p-3 text-left hover:border-primary-400 dark:border-surface-700 dark:bg-surface-800 dark:hover:border-primary-500"
          >
            <p className="text-xs font-medium text-surface-900 dark:text-surface-50">{t.name}</p>
            <p className="mt-0.5 text-[11px] text-surface-500">{t.description}</p>
          </button>
        ))}
      </div>
    </div>
  );
}