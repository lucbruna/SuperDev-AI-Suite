# Using Agents

## List Available Agents

```bash
superdev agent list
```

## Start an Agent

```bash
superdev agent start architect-agent
```

## View Agent Logs

```bash
superdev agent logs architect-agent
```

## Agent Types

| Agent | Description |
|-------|-------------|
| `architect-agent` | System design and architecture |
| `executor-agent` | Code execution |
| `reviewer-agent` | Code review |
| `testing-agent` | Test generation |
| `documentation-agent` | Documentation |
| `security-agent` | Security analysis |
| `deployment-agent` | Deployment automation |

## Using Agents via API

```python
from superdev_sdk import SuperDevClient

client = SuperDevClient(api_key="sk-...")

# Start an agent
agent = client.agents.start("architect-agent")

# Chat with agent
response = client.chat.send(
    "Design a microservices architecture for an e-commerce platform",
    model="gpt-4"
)
```
