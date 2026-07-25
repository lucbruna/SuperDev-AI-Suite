#!/bin/bash
set -euo pipefail

echo "Running infrastructure tests..."

# Test Docker
docker info > /dev/null 2>&1
echo "✓ Docker is available"

# Test docker-compose
docker-compose version > /dev/null 2>&1
echo "✓ docker-compose is available"

# Test Terraform
terraform version > /dev/null 2>&1
echo "✓ Terraform is available"

# Test Ansible
ansible --version > /dev/null 2>&1
echo "✓ Ansible is available"

# Test network connectivity
curl -sf http://localhost:8000/health > /dev/null 2>&1 || echo "⚠ Backend not running"
curl -sf http://localhost:3000 > /dev/null 2>&1 || echo "⚠ Frontend not running"

echo "Infrastructure tests completed"
