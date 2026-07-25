# SuperDev Go SDK

Go client library for the SuperDev AI Suite API.

## Installation

```bash
go get github.com/superdev/sdk-go
```

## Quick Start

```go
package main

import (
    "fmt"
    superdev "github.com/superdev/sdk-go"
)

func main() {
    client := superdev.NewClient("http://localhost:8000", "sk-...")

    // List projects
    projects, err := client.Projects.List(1, 20)
    if err != nil {
        panic(err)
    }
    fmt.Println(projects.Items)

    // Chat with AI
    response, err := client.Chat.Send("Hello!", "")
    if err != nil {
        panic(err)
    }
    fmt.Println(response.Message)
}
```

## Error Handling

```go
response, err := client.Projects.Get("proj_123")
if err != nil {
    var apiErr *superdev.APIError
    if errors.As(err, &apiErr) {
        if apiErr.IsNotFound() {
            fmt.Println("Not found")
        }
    }
}
```
