#!/bin/bash
set -euo pipefail

echo "Setting up SuperDev infrastructure..."

# Check dependencies
command -v docker >/dev/null 2>&1 || { echo "docker not found"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "docker-compose not found"; exit 1; }

# Create networks
docker network create superdev 2>/dev/null || true

# Create volumes
docker volume create postgres_data 2>/dev/null || true
docker volume create redis_data 2>/dev/null || true

# Start services
docker-compose up -d

echo "Infrastructure is ready!"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo "  Grafana:  http://localhost:3001"
