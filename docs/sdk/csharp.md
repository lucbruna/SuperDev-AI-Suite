# C# SDK

## Installation

```bash
dotnet add package SuperDev.SDK
```

## Usage

```csharp
using SuperDev.SDK;

var client = new SuperDevClient("http://localhost:8000", "sk-...");

var me = await client.Users.MeAsync();
var projects = await client.Projects.ListAsync();
var response = await client.Chat.SendAsync("Hello!");
Console.WriteLine(response.Message);
```
