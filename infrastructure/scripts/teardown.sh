#!/bin/bash
set -euo pipefail

echo "Tearing down SuperDev infrastructure..."

docker-compose down -v

docker network rm superdev 2>/dev/null || true

echo "Infrastructure torn down"
