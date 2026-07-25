# Contributing to SuperDev AI Suite

First off, thank you for considering contributing to SuperDev AI Suite. It's people like you that make SuperDev such a great tool.

## How to Contribute

### Reporting Bugs

- Ensure the bug was not already reported by searching on GitHub under Issues
- If you're unable to find an open issue addressing the problem, open a new one
- Include a clear title, description, steps to reproduce, expected behavior, and actual behavior
- Include code samples, screenshots, or logs if applicable

### Suggesting Enhancements

- Open a new issue with a clear title and detailed description
- Explain why this enhancement would be useful to most users
- Include mockups or examples if applicable

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Node.js 20 LTS or higher
- pnpm 9 or higher
- Docker Desktop 24+
- PostgreSQL 16 (or use Docker)

### Local Setup

```bash
# Clone your fork
git clone https://github.com/your-username/superdev-ai-suite.git
cd superdev-ai-suite

# Install Python dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"

# Install frontend dependencies
pnpm install

# Copy environment file
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start development servers
make dev
```

## Coding Standards

### Python

- Follow PEP 8 conventions
- Use type hints for all function signatures
- Maximum line length: 120 characters
- Use ruff for linting and formatting
- Write docstrings for all public modules, functions, classes, and methods
- Use async/await for I/O-bound operations

### TypeScript / JavaScript

- Follow the project's ESLint configuration
- Use TypeScript strict mode
- Maximum line length: 120 characters
- Use Prettier for formatting
- Use functional components with hooks in React

### General

- Write tests for all new code
- Ensure all existing tests pass before submitting
- Keep pull requests focused on a single concern
- Rebase your branch on the latest main before submitting

## PR Process

1. Ensure your code passes all linting and type checks: `make lint && make typecheck`
2. Run the full test suite: `make test`
3. Update documentation if you're adding or changing features
4. Add a changelog entry
5. Your PR should be reviewed by at least one maintainer
6. Address any review feedback promptly
7. Once approved, a maintainer will merge your PR

Thank you for contributing!
