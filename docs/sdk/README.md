# SuperDev SDKs

Official client libraries for integrating with SuperDev.

## Available SDKs

| Language | Package | Install |
|----------|---------|---------|
| Python | `superdev-sdk` | `pip install superdev-sdk` |
| TypeScript | `superdev-sdk` | `npm install superdev-sdk` |
| Go | `github.com/superdev/sdk-go` | `go get github.com/superdev/sdk-go` |
| Java | `com.superdev:sdk` | Maven dependency |
| Rust | `superdev-sdk` | `cargo add superdev-sdk` |
| C# | `SuperDev.SDK` | NuGet package |

## Quick Examples

### Python
```python
from superdev_sdk import SuperDevClient

client = SuperDevClient(api_key="sk-...")
projects = client.projects.list()
response = client.chat.send("Hello!")
```

### TypeScript
```typescript
import { SuperDevClient } from "superdev-sdk";

const client = new SuperDevClient({ apiKey: "sk-..." });
const projects = await client.projects.list();
```

### Go
```go
client := superdev.NewClient("http://localhost:8000", "sk-...")
projects, _ := client.Projects.List(1, 20)
```

## Documentation

- [Python SDK](python.md)
- [TypeScript SDK](typescript.md)
- [Go SDK](go.md)
- [Java SDK](java.md)
- [Rust SDK](rust.md)
- [C# SDK](csharp.md)
