# SuperDev Rust SDK

Rust client library for the SuperDev AI Suite API.

## Installation

```toml
[dependencies]
superdev-sdk = "0.1.0"
```

## Quick Start

```rust
use superdev_sdk::SuperDevClient;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = SuperDevClient::new("http://localhost:8000", "sk-...");

    // List projects
    let projects = client.list_projects(1, 20).await?;
    println!("{:?}", projects.items);

    // Chat with AI
    let response = client.send_chat("Hello!", None).await?;
    println!("{}", response.message);

    Ok(())
}
```

## Features

- Full async support with tokio
- Typed responses with serde
- Streaming support
