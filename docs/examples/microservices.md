# Microservices Example

A distributed system with multiple services.

## Setup

```bash
superdev init my-microservices --example microservices
cd my-microservices
docker-compose up
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| api-gateway | 8000 | Entry point |
| user-service | 8001 | User management |
| product-service | 8002 | Product catalog |
| order-service | 8003 | Order processing |
| notification-service | 8004 | Notifications |

## Architecture

- API Gateway routes requests
- Each service has its own database
- Redis for inter-service communication
- Docker Compose for local development
