# Python SDK

## Installation

```bash
pip install superdev-sdk

# With async support
pip install superdev-sdk[async]
```

## Configuration

```python
from superdev_sdk import SuperDevClient

# With API key
client = SuperDevClient(api_key="sk-...")

# With base URL
client = SuperDevClient("http://localhost:8000", api_key="sk-...")

# With login
client = SuperDevClient("http://localhost:8000")
client.login(email="user@example.com", password="password")
```

## Resources

### Users
```python
me = client.users.me()
users = client.users.list(page=1, page_size=20)
```

### Projects
```python
projects = client.projects.list()
project = client.projects.get("proj_123")
new_project = client.projects.create("My Project", "Description")
client.projects.delete("proj_123")
```

### Agents
```python
agents = client.agents.list()
agent = client.agents.get("agent_123")
client.agents.start("agent_123")
client.agents.stop("agent_123")
```

### Workflows
```python
workflows = client.workflows.list()
run = client.workflows.run("wf_123", inputs={"key": "value"})
```

### Chat
```python
response = client.chat.send("Hello!", model="gpt-4")
for chunk in client.chat.stream("Tell me a story"):
    print(chunk.delta, end="")
```

## Error Handling

```python
from superdev_sdk.exceptions import AuthenticationError, NotFoundError

try:
    project = client.projects.get("nonexistent")
except NotFoundError:
    print("Not found")
except AuthenticationError:
    print("Auth failed")
```
