# Creating Workflows

## Via CLI

```bash
superdev workflow create
```

This opens an interactive prompt to define your workflow.

## Via API

```python
from superdev_sdk import SuperDevClient

client = SuperDevClient(api_key="sk-...")

workflow = client.workflows.create(
    name="Deploy Pipeline",
    graph={
        "nodes": [
            {"id": "build", "type": "shell", "command": "npm run build"},
            {"id": "test", "type": "shell", "command": "npm test"},
            {"id": "deploy", "type": "shell", "command": "superdev deploy"},
        ],
        "edges": [
            {"from": "build", "to": "test"},
            {"from": "test", "to": "deploy"},
        ],
    },
)

# Run the workflow
run = client.workflows.run(workflow.id, inputs={"env": "staging"})
```

## Workflow Node Types

| Type | Description |
|------|-------------|
| `shell` | Execute shell commands |
| `python` | Run Python code |
| `agent` | Invoke an AI agent |
| `http` | Make HTTP requests |
| `condition` | Conditional branching |
| `loop` | Iterate over items |
| `parallel` | Run nodes in parallel |
| `approval` | Human approval gate |
