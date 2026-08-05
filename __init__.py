"""
SuperDev AI Suite v6 Enterprise
===============================

An enterprise-grade AI-powered development platform that provides:
- AI-powered code generation and assistance
- Multi-agent orchestration for complex development tasks
- Visual workflow editor for CI/CD and data pipelines
- Real-time collaboration features
- Enterprise security and compliance tools
- Extensible plugin architecture
- Native cloud runtime with Kubernetes support

Main Components:
- backend: FastAPI-based REST API and WebSocket services
- frontend: Next.js 14 web application (official UI)
- admin-dashboard: Legacy Vite + React admin panel
- desktop: Cross-platform desktop application
- mobile: React Native/Flutter mobile clients
- cli: Command-line interface
- sdk: Official SDKs (Python, TypeScript, Go, Rust, Java)
- agents: Specialized AI agents (Architect, Backend, Frontend, etc.)
- workflow: Workflow engine and orchestration system
- runtime: Isolated execution environment
- plugins: Plugin marketplace and management system
- ai_router: AI provider routing and load balancing
- knowledge: Knowledge base and vector search
- database: ORM models and migrations
- security: Authentication, encryption, and vault
- observability: Logging, tracing, and metrics
- monitoring: Alerts, dashboards, and status
- testing: Unit, integration, and end-to-end tests
- docs: Documentation
- examples: Example projects
- templates: Project templates
- scripts: Build and deployment scripts
- tools: Development utilities

Version: 6.0.0
Author: SuperDev Team
License: MIT
"""

__version__ = "6.0.0"
__author__ = "SuperDev Team"
__email__ = "dev@superdev.com"
__license__ = "MIT"
__status__ = "Production"

# Package metadata
__title__ = "SuperDev AI Suite"
__description__ = "Enterprise-grade AI-powered development platform"
__url__ = "https://github.com/lucbruna/SuperDev-AI-Suite"

# Import key components for easy access
# from .backend import app  # Uncomment when backend module is structured
# from .frontend import app  # Uncomment when frontend module is structured

# Public API
__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__status__",
    "__title__",
    "__description__",
    "__url__",
]