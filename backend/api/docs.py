"""API documentation configuration — OpenAPI metadata, tags, Swagger UI."""

from starlette.applications import Starlette

OPENAPI_TAGS = [
    {
        "name": "Authentication",
        "description": "User authentication, registration, JWT tokens, API keys",
    },
    {
        "name": "Users",
        "description": "User profile management, preferences, avatar",
    },
    {
        "name": "Projects",
        "description": "Project CRUD, members, settings, environments",
    },
    {
        "name": "Workflows",
        "description": "Workflow design, execution, DAG management, versioning",
    },
    {
        "name": "Agents",
        "description": "AI agent creation, configuration, execution, templates",
    },
    {
        "name": "Plugins",
        "description": "Plugin marketplace, installation, lifecycle, hooks",
    },
    {
        "name": "Providers",
        "description": "LLM provider configuration, key management, routing",
    },
    {
        "name": "Knowledge",
        "description": "RAG knowledge base, documents, embeddings, search",
    },
    {
        "name": "Notifications",
        "description": "User notifications, channels, preferences",
    },
    {
        "name": "Audit",
        "description": "Audit logs, compliance trails, activity tracking",
    },
    {
        "name": "Organizations",
        "description": "Organization management, invitations, billing",
    },
    {
        "name": "Health",
        "description": "System health checks, readiness, liveness probes",
    },
    {
        "name": "API Keys",
        "description": "API key management, rotation, scopes",
    },
]


def setup_docs(app: Starlette) -> None:
    """Configure OpenAPI metadata, Swagger UI, and ReDoc on a Starlette/FastAPI app."""
    app.title = "SuperDev AI Suite"
    app.version = "6.0.0"
    app.description = (
        "Enterprise-grade AI-powered development platform with autonomous "
        "workflows, multi-model agent orchestration, RAG knowledge base, "
        "plugin ecosystem, real-time collaboration, and advanced analytics."
    )
    app.openapi_tags = OPENAPI_TAGS
    app.contact = {
        "name": "SuperDev Team",
        "email": "team@superdev.ai",
        "url": "https://superdev.ai",
    }
    app.license_info = {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
