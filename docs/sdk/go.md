# Go SDK

## Installation

```bash
go get github.com/superdev/sdk-go
```

## Usage

```go
package main

import (
    "fmt"
    superdev "github.com/superdev/sdk-go"
)

func main() {
    client := superdev.NewClient("http://localhost:8000", "sk-...")

    projects, err := client.Projects.List(1, 20)
    if err != nil {
        panic(err)
    }
    fmt.Println(projects.Items)

    response, err := client.Chat.Send("Hello!", "")
    if err != nil {
        panic(err)
    }
    fmt.Println(response.Message)
}
```
