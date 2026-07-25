# Rust SDK

## Installation

```toml
[dependencies]
superdev-sdk = "0.1.0"
```

## Usage

```rust
use superdev_sdk::SuperDevClient;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = SuperDevClient::new("http://localhost:8000", "sk-...");

    let projects = client.list_projects(1, 20).await?;
    println!("{:?}", projects.items);

    let response = client.send_chat("Hello!", None).await?;
    println!("{}", response.message);

    Ok(())
}
```
