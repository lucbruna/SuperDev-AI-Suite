# TypeScript SDK

## Installation

```bash
npm install superdev-sdk
```

## Usage

```typescript
import { SuperDevClient } from "superdev-sdk";

const client = new SuperDevClient({
  baseUrl: "http://localhost:8000",
  apiKey: "sk-...",
});

// List projects
const projects = await client.projects.list();

// Chat
const response = await client.chat.send("Hello!");
console.log(response.message);

// Stream
for await (const chunk of client.chat.stream("Tell me a story")) {
  process.stdout.write(chunk.delta);
}
```

## Error Handling

```typescript
import { NotFoundError, AuthenticationError } from "superdev-sdk";

try {
  await client.projects.get("nonexistent");
} catch (e) {
  if (e instanceof NotFoundError) console.log("Not found");
}
```
