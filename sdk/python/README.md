# SuperDev Python SDK

Client library for the SuperDev AI Suite API.

## Installation

```bash
pip install superdev-sdk

# With async support
pip install superdev-sdk[async]
```

## Quick Start

### Synchronous

```python
from superdev_sdk import SuperDevClient

client = SuperDevClient("http://localhost:8000", api_key="sk-...")

# List projects
projects = client.projects.list()

# Chat with AI
response = client.chat.send("Hello, what can you do?")
print(response.message)

# Stream responses
for chunk in client.chat.stream("Tell me a story"):
    print(chunk.delta, end="")
```

### Asynchronous

```python
from superdev_sdk import AsyncSuperDevClient

async with AsyncSuperDevClient("http://localhost:8000", api_key="sk-...") as client:
    projects = await client.projects.list()
    response = await client.chat.send("Hello!")
    print(response.message)
```

### Authentication

```python
# With API key
client = SuperDevClient(api_key="sk-...")

# With login
client = SuperDevClient("http://localhost:8000")
client.login(email="user@example.com", password="password")
```

## Error Handling

```python
from superdev_sdk import SuperDevClient
from superdev_sdk.exceptions import AuthenticationError, NotFoundError

client = SuperDevClient(api_key="sk-...")

try:
    project = client.projects.get("proj_123")
except NotFoundError:
    print("Project not found")
except AuthenticationError:
    print("Invalid credentials")
```

## Available Resources

| Resource | Description |
|----------|-------------|
| `client.users` | User management |
| `client.projects` | Project CRUD |
| `client.agents` | Agent control |
| `client.workflows` | Workflow management |
| `client.providers` | AI provider configuration |
| `client.plugins` | Plugin management |
| `client.chat` | Chat and embeddings |
| `client.deployments` | Deployment management |
