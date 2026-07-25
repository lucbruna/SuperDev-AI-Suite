#!/bin/bash
# SuperDev AI Suite - Development Setup Script
# This script sets up the complete development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 SuperDev AI Suite - Development Setup${NC}"
echo "=========================================="

# Check prerequisites
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✅ $1 found${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 is not installed${NC}"
        return 1
    fi
}

echo -e "\n${YELLOW}Checking prerequisites...${NC}"
MISSING=0

check_command "docker" || MISSING=1
check_command "docker-compose" || MISSING=1
check_command "python3" || MISSING=1
check_command "poetry" || MISSING=1
check_command "node" || MISSING=1
check_command "npm" || MISSING=1
check_command "go" || MISSING=1
check_command "cargo" || MISSING=1
check_command "kubectl" || MISSING=1
check_command "helm" || MISSING=1
check_command "terraform" || MISSING=1

if [ $MISSING -ne 0 ]; then
    echo -e "\n${RED}Please install missing prerequisites before continuing${NC}"
    exit 1
fi

# Create .env file if not exists
if [ ! -f .env ]; then
    echo -e "\n${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ .env created - please edit with your values${NC}"
else
    echo -e "\n${GREEN}✅ .env already exists${NC}"
fi

# Start infrastructure
echo -e "\n${YELLOW}Starting infrastructure (PostgreSQL + Redis)...${NC}"
docker-compose -f infrastructure/docker/docker-compose.yml up -d postgres redis

# Wait for services
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Check PostgreSQL
until docker-compose -f infrastructure/docker/docker-compose.yml exec -T postgres pg_isready -U superdev -d superdev > /dev/null 2>&1; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done
echo -e "${GREEN}✅ PostgreSQL ready${NC}"

# Check Redis
until docker-compose -f infrastructure/docker/docker-compose.yml exec -T redis redis-cli ping > /dev/null 2>&1; do
    echo "Waiting for Redis..."
    sleep 2
done
echo -e "${GREEN}✅ Redis ready${NC}"

# Setup Python backend
echo -e "\n${YELLOW}Setting up Python backend...${NC}"
cd backend
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev,test]"
cd ..

# Run database migrations
echo -e "\n${YELLOW}Running database migrations...${NC}"
cd backend
source .venv/bin/activate
alembic upgrade head
cd ..

# Setup Node.js frontend
echo -e "\n${YELLOW}Setting up Node.js frontend...${NC}"
cd admin-dashboard
npm ci
cd ..

# Setup Go SDK
echo -e "\n${YELLOW}Setting up Go SDK...${NC}"
cd sdk/go
go mod tidy
go build ./...
cd ../..

# Setup Rust SDK
echo -e "\n${YELLOW}Setting up Rust SDK...${NC}"
cd sdk/rust
cargo build
cd ../..

# Setup Python SDK
echo -e "\n${YELLOW}Setting up Python SDK...${NC}"
cd sdk/python
pip install -e .
cd ../..

# Run tests
echo -e "\n${YELLOW}Running tests...${NC}"
cd backend
source .venv/bin/activate
pytest tests/ -v --tb=short
cd ..

cd admin-dashboard
npm run test
cd ..

# Build Docker images
echo -e "\n${YELLOW}Building Docker images...${NC}"
docker build -t ghcr.io/superdev/superdev-api:latest -f infrastructure/docker/Dockerfile.api .
docker build -t ghcr.io/superdev/superdev-frontend:latest -f infrastructure/docker/Dockerfile.frontend .
docker build -t ghcr.io/superdev/superdev-worker:latest -f infrastructure/docker/Dockerfile.worker .
docker build -t ghcr.io/superdev/superdev-sandbox:latest -f infrastructure/docker/Dockerfile.sandbox .

echo -e "\n${GREEN}✅ Development environment setup complete!${NC}"
echo -e "\n${BLUE}Next steps:${NC}"
echo "1. Edit .env with your configuration"
echo "2. Start the development server: make run"
echo "2. Access the dashboard at http://localhost:3000"
echo "3. API docs at http://localhost:8000/docs"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"