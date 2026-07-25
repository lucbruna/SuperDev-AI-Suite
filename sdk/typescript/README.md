# SuperDev TypeScript SDK

TypeScript client library for the SuperDev AI Suite API.

## Installation

```bash
npm install superdev-sdk
# or
pnpm add superdev-sdk
```

## Quick Start

```typescript
import { SuperDevClient } from "superdev-sdk";

const client = new SuperDevClient({
  baseUrl: "http://localhost:8000",
  apiKey: "sk-...",
});

// List projects
const projects = await client.projects.list();

// Chat with AI
const response = await client.chat.send({ message: "Hello, what can you do?" });
console.log(response.message);

// Stream responses
for await (const chunk of await client.chat.stream({ message: "Tell me a story" })) {
  process.stdout.write(chunk.delta);
}
```

## Authentication

### API Key

```typescript
const client = new SuperDevClient({
  baseUrl: "http://localhost:8000",
  apiKey: "sk-...",
});
```

### Email / Password Login

```typescript
const client = new SuperDevClient({ baseUrl: "http://localhost:8000" });
await client.login("user@example.com", "password");

// ... use client ...

client.logout();
```

## Error Handling

```typescript
import { NotFoundError, AuthenticationError } from "superdev-sdk";

try {
  const project = await client.projects.get("proj_123");
} catch (err) {
  if (err instanceof NotFoundError) {
    console.log("Project not found");
  } else if (err instanceof AuthenticationError) {
    console.log("Invalid credentials");
  }
}
```

### Error Hierarchy

| Class                 | HTTP Status | Description                    |
| --------------------- | ----------- | ------------------------------ |
| `SuperDevError`       | (base)      | Base error for all SDK errors  |
| `AuthenticationError` | 401         | Invalid or missing credentials |
| `AuthorizationError`  | 403         | Permission denied              |
| `NotFoundError`       | 404         | Resource not found             |
| `ValidationError`     | 422         | Invalid request data           |
| `RateLimitError`      | 429         | Too many requests              |
| `ServerError`         | 500         | Internal server error          |
| `ConnectionError`     | (network)   | Cannot reach server            |
| `TimeoutError`        | (network)   | Request timed out              |

## Streaming

```typescript
import { StreamProcessor } from "superdev-sdk";

const processor = new StreamProcessor();
processor
  .onChunk((chunk) => process.stdout.write(chunk.delta))
  .onComplete((usage) => console.log("\nTokens:", usage));

const stream = await client.chat.stream({ message: "Write a poem" });
for await (const chunk of stream) {
  processor.process(chunk);
}

console.log(processor.fullText);
```

## Utilities

```typescript
import { retry, truncate, slugify, formatTokens } from "superdev-sdk";

// Retry with exponential backoff
const data = await retry(() => client.projects.get("proj_1"), {
  maxRetries: 3,
  delay: 1000,
});

truncate("Hello, World!", 5);  // "He..."
slugify("Hello World!");        // "hello-world"
formatTokens(1500);             // "1.5K"
```

## Resources

| Resource             | Description                     |
| -------------------- | ------------------------------- |
| `client.users`       | User management                 |
| `client.projects`    | Project CRUD                    |
| `client.agents`      | Agent lifecycle control         |
| `client.workflows`   | Workflow CRUD and execution     |
| `client.providers`   | AI provider configuration       |
| `client.plugins`     | Plugin install/uninstall/update |
| `client.chat`        | Chat, streaming, and embeddings |
| `client.deployments` | Deployment management           |

## TypeScript Support

The SDK is written in strict TypeScript with full type safety:

- All API responses are fully typed
- `PaginatedResponse<T>` is generic over the resource type
- Input types are defined for every mutation endpoint
- No `any` types — all dynamic data uses `Record<string, unknown>`

## Requirements

- Node.js >= 18 (for native `fetch`)
- TypeScript >= 5.0
