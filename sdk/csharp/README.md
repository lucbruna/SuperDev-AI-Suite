# SuperDev C# SDK

Official C# client for the SuperDev AI Suite API.

## Installation

```bash
dotnet add package SuperDev.SDK
```

## Quick Start

```csharp
using SuperDev.SDK;
using SuperDev.SDK.Models;

// Direct instantiation
var client = SuperDevClient.Create(
    baseUrl: "http://localhost:8000",
    apiKey: "sk-your-api-key");

// List projects
var projects = await client.Projects.ListAsync();
foreach (var project in projects.Items)
    Console.WriteLine($"{project.Name} ({project.Id})");

// Chat
var response = await client.Chat.SendAsync("Hello, SuperDev!");
Console.WriteLine(response.Message);
```

## Dependency Injection

```csharp
// Program.cs / Startup.cs
builder.Services.AddSuperDevSDK(options =>
{
    options.BaseUrl = "http://localhost:8000";
    options.ApiKey = "sk-your-api-key";
});

// Inject SuperDevClient via constructor
public class MyService(SuperDevClient client)
{
    public async Task<User> GetCurrentUser()
        => await client.Users.MeAsync();
}
```

## Authentication

```csharp
// API Key
var client = SuperDevClient.Create(apiKey: "sk-...");

// Login with email/password
var user = await client.LoginAsync("user@example.com", "password");
// Tokens are stored automatically; subsequent requests use them.

// Logout
client.Logout();
```

## Available APIs

| Property | Methods |
|----------|---------|
| `client.Users` | `MeAsync()`, `ListAsync(page, pageSize)` |
| `client.Projects` | `ListAsync()`, `GetAsync(id)`, `CreateAsync(name, desc)`, `UpdateAsync(id, updates)`, `DeleteAsync(id)` |
| `client.Agents` | `ListAsync()`, `GetAsync(id)`, `StartAsync(id, config)`, `StopAsync(id)`, `LogsAsync(id, limit)` |
| `client.Workflows` | `ListAsync()`, `GetAsync(id)`, `CreateAsync(name, graph)`, `RunAsync(id, inputs)`, `GetRunAsync(id, runId)`, `CancelRunAsync(id, runId)`, `DeleteAsync(id)` |
| `client.Providers` | `ListAsync()`, `HealthAsync(id)`, `EnableAsync(id)`, `DisableAsync(id)`, `ConfigureAsync(id, config)` |
| `client.Plugins` | `ListAsync()`, `InstallAsync(id)`, `UninstallAsync(id)`, `UpdateAsync(id)` |
| `client.Chat` | `SendAsync(message, ...)`, `StreamAsync(message, ...)`, `ConversationsAsync()`, `EmbeddingsAsync(input)` |

## Streaming

```csharp
await foreach (var chunk in client.Chat.StreamAsync("Tell me a story"))
{
    Console.Write(chunk.Delta);
    if (chunk.FinishReason is not null)
        Console.WriteLine($"\n[Done: {chunk.FinishReason}]");
}
```

## Error Handling

```csharp
using SuperDev.SDK.Exceptions;

try
{
    var project = await client.Projects.GetAsync("nonexistent-id");
}
catch (NotFoundException ex)
{
    Console.WriteLine($"Not found: {ex.Message}");
}
catch (AuthenticationException ex)
{
    Console.WriteLine($"Auth error: {ex.Message}");
}
catch (SuperDevException ex)
{
    Console.WriteLine($"API error ({ex.StatusCode}): {ex.Message}");
}
```

## Requirements

- .NET 8.0+
