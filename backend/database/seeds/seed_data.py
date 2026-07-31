"""
Seed data realista para o SuperDev.
Alinhado com os modelos ORM atuais (users, organizations, projects, agents, workflows, providers, plugins).
"""

from __future__ import annotations

from typing import Any

# UUIDs determinísticos para referência entre tabelas
IDS = {
    # Users
    "admin": "00000000-0000-0000-0000-000000000001",
    "dev": "00000000-0000-0000-0000-000000000002",
    "user": "00000000-0000-0000-0000-000000000003",
    # Organizations
    "superdev": "00000000-0000-0000-0000-000000000010",
    "startup": "00000000-0000-0000-0000-000000000011",
    # Projects
    "erp": "00000000-0000-0000-0000-000000000020",
    "chatbot": "00000000-0000-0000-0000-000000000021",
    "api_gateway": "00000000-0000-0000-0000-000000000022",
    # Agents
    "architect": "00000000-0000-0000-0000-000000000030",
    "executor": "00000000-0000-0000-0000-000000000031",
    "reviewer": "00000000-0000-0000-0000-000000000032",
    "tester": "00000000-0000-0000-0000-000000000033",
    # Workflows
    "deploy": "00000000-0000-0000-0000-000000000040",
    "code_review": "00000000-0000-0000-0000-000000000041",
    # Providers
    "openai": "00000000-0000-0000-0000-000000000050",
    "anthropic": "00000000-0000-0000-0000-000000000051",
    "ollama": "00000000-0000-0000-0000-000000000052",
    # Plugins
    "git": "00000000-0000-0000-0000-000000000060",
    "docker": "00000000-0000-0000-0000-000000000061",
    "database": "00000000-0000-0000-0000-000000000062",
    # Roles (mesmos UUIDs de roles.py)
    "super_admin": "00000000-0000-0000-0000-000000000100",
    "role_admin": "00000000-0000-0000-0000-000000000101",
    "developer": "00000000-0000-0000-0000-000000000102",
    "viewer": "00000000-0000-0000-0000-000000000103",
}


def uuid_str(key: str) -> str:
    return IDS[key]


# ── Usuários ──────────────────────────────────────────────────────

USERS: list[dict[str, Any]] = [
    {
        "id": uuid_str("admin"),
        "email": "admin@superdev.com",
        "username": "admin",
        "hashed_password": "$2b$12$D.2durRQxgfKWD0Kofv5S.Cl5CarCy1VPTrPiIlIOef/bG8YUQoF6",
        "full_name": "Administrador",
        "is_active": True,
        "is_superuser": True,
        "is_verified": True,
    },
    {
        "id": uuid_str("dev"),
        "email": "dev@superdev.com",
        "username": "dev",
        "hashed_password": "$2b$12$D.2durRQxgfKWD0Kofv5S.Cl5CarCy1VPTrPiIlIOef/bG8YUQoF6",
        "full_name": "Desenvolvedor Principal",
        "is_active": True,
        "is_superuser": False,
        "is_verified": True,
    },
    {
        "id": uuid_str("user"),
        "email": "usuario@superdev.com",
        "username": "usuario",
        "hashed_password": "$2b$12$D.2durRQxgfKWD0Kofv5S.Cl5CarCy1VPTrPiIlIOef/bG8YUQoF6",
        "full_name": "Usuário Padrão",
        "is_active": True,
        "is_superuser": False,
        "is_verified": True,
    },
]

# ── Organizações ──────────────────────────────────────────────────

ORGANIZATIONS: list[dict[str, Any]] = [
    {
        "id": uuid_str("superdev"),
        "name": "SuperDev Corp",
        "slug": "superdev-corp",
        "description": "Empresa líder em soluções de desenvolvimento com IA",
        "plan": "enterprise",
        "settings": {
            "features": ["multi_agent", "workflow_automation", "custom_plugins"],
            "max_users": 100,
            "storage_gb": 500,
        },
    },
    {
        "id": uuid_str("startup"),
        "name": "Startup Labs",
        "slug": "startup-labs",
        "description": "Incubadora de startups de tecnologia",
        "plan": "pro",
        "settings": {
            "features": ["multi_agent", "workflow_automation"],
            "max_users": 25,
            "storage_gb": 100,
        },
    },
]

# ── Membros de Organizações ──────────────────────────────────────

ORGANIZATION_MEMBERS: list[dict[str, Any]] = [
    {
        "organization_id": uuid_str("superdev"),
        "user_id": uuid_str("admin"),
        "role": "owner",
    },
    {
        "organization_id": uuid_str("superdev"),
        "user_id": uuid_str("dev"),
        "role": "admin",
    },
    {
        "organization_id": uuid_str("superdev"),
        "user_id": uuid_str("user"),
        "role": "member",
    },
    {
        "organization_id": uuid_str("startup"),
        "user_id": uuid_str("dev"),
        "role": "owner",
    },
]

# ── Projetos ──────────────────────────────────────────────────────

PROJECTS: list[dict[str, Any]] = [
    {
        "id": uuid_str("erp"),
        "name": "Sistema ERP Completo",
        "slug": "sistema-erp-completo",
        "description": "Sistema de gestão empresarial com módulos financeiro, estoque e RH",
        "visibility": "private",
        "organization_id": uuid_str("superdev"),
        "owner_id": uuid_str("admin"),
        "settings": {
            "language": "python",
            "framework": "fastapi",
            "database": "postgresql",
            "frontend": "react",
        },
    },
    {
        "id": uuid_str("chatbot"),
        "name": "Chatbot Atendimento",
        "slug": "chatbot-atendimento",
        "description": "Chatbot inteligente para atendimento ao cliente",
        "visibility": "private",
        "organization_id": uuid_str("superdev"),
        "owner_id": uuid_str("dev"),
        "settings": {
            "language": "python",
            "framework": "fastapi",
            "ai_provider": "openai",
            "model": "gpt-4",
        },
    },
    {
        "id": uuid_str("api_gateway"),
        "name": "API Gateway",
        "slug": "api-gateway",
        "description": "Gateway de APIs com rate limiting e autenticação",
        "visibility": "private",
        "organization_id": uuid_str("startup"),
        "owner_id": uuid_str("dev"),
        "settings": {
            "language": "typescript",
            "framework": "express",
            "database": "redis",
        },
    },
]

# ── User Roles ───────────────────────────────────────────────────

USER_ROLES: list[dict[str, Any]] = [
    {
        "user_id": uuid_str("admin"),
        "role_id": uuid_str("super_admin"),
        "organization_id": uuid_str("superdev"),
    },
    {
        "user_id": uuid_str("dev"),
        "role_id": uuid_str("developer"),
        "organization_id": uuid_str("superdev"),
    },
    {
        "user_id": uuid_str("dev"),
        "role_id": uuid_str("super_admin"),
        "organization_id": uuid_str("startup"),
    },
    {
        "user_id": uuid_str("user"),
        "role_id": uuid_str("viewer"),
        "organization_id": uuid_str("superdev"),
    },
]

# ── Membros de Projetos ──────────────────────────────────────────

PROJECT_MEMBERS: list[dict[str, Any]] = [
    {"project_id": uuid_str("erp"), "user_id": uuid_str("admin"), "role": "owner"},
    {"project_id": uuid_str("erp"), "user_id": uuid_str("dev"), "role": "admin"},
    {"project_id": uuid_str("erp"), "user_id": uuid_str("user"), "role": "member"},
    {"project_id": uuid_str("chatbot"), "user_id": uuid_str("dev"), "role": "owner"},
    {"project_id": uuid_str("chatbot"), "user_id": uuid_str("user"), "role": "member"},
    {"project_id": uuid_str("api_gateway"), "user_id": uuid_str("dev"), "role": "owner"},
]

# ── Agentes ───────────────────────────────────────────────────────

AGENTS: list[dict[str, Any]] = [
    {
        "id": uuid_str("architect"),
        "name": "Architect Agent",
        "type": "architect",
        "description": "Agente especializado em arquitetura de software e design patterns",
        "config": {"capabilities": ["architecture", "design_patterns", "code_review"], "max_tokens": 4096},
        "model_provider": "openai",
        "model_name": "gpt-4",
        "tools": ["code_reader", "diagram_generator", "file_reader"],
        "is_active": True,
        "project_id": uuid_str("erp"),
        "created_by": uuid_str("admin"),
    },
    {
        "id": uuid_str("executor"),
        "name": "Executor Agent",
        "type": "executor",
        "description": "Agente especializado em geração e refatoração de código",
        "config": {"capabilities": ["code_generation", "refactoring", "debugging"], "max_tokens": 8192},
        "model_provider": "openai",
        "model_name": "gpt-4",
        "tools": ["code_writer", "file_reader", "terminal"],
        "is_active": True,
        "project_id": uuid_str("erp"),
        "created_by": uuid_str("admin"),
    },
    {
        "id": uuid_str("reviewer"),
        "name": "Reviewer Agent",
        "type": "reviewer",
        "description": "Agente especializado em code review e auditoria de segurança",
        "config": {"capabilities": ["code_review", "security_audit", "performance"], "max_tokens": 4096},
        "model_provider": "anthropic",
        "model_name": "claude-3-sonnet",
        "tools": ["code_reader", "security_scanner", "performance_analyzer"],
        "is_active": True,
        "project_id": uuid_str("chatbot"),
        "created_by": uuid_str("dev"),
    },
    {
        "id": uuid_str("tester"),
        "name": "Testing Agent",
        "type": "tester",
        "description": "Agente especializado em testes automatizados",
        "config": {"capabilities": ["unit_testing", "integration_testing", "e2e_testing"], "max_tokens": 4096},
        "model_provider": "openai",
        "model_name": "gpt-4",
        "tools": ["test_runner", "code_reader", "file_writer"],
        "is_active": True,
        "project_id": uuid_str("chatbot"),
        "created_by": uuid_str("dev"),
    },
]

# ── Workflows ─────────────────────────────────────────────────────

WORKFLOWS: list[dict[str, Any]] = [
    {
        "id": uuid_str("deploy"),
        "name": "Pipeline de Deploy",
        "description": "Pipeline completo de CI/CD para produção",
        "definition": {
            "nodes": [
                {"id": "build", "type": "shell", "command": "npm run build"},
                {"id": "test", "type": "shell", "command": "npm test"},
                {"id": "lint", "type": "shell", "command": "npm run lint"},
                {"id": "deploy_staging", "type": "shell", "command": "npm run deploy:staging"},
                {"id": "approve", "type": "human", "prompt": "Aprovar deploy para produção?"},
                {"id": "deploy_prod", "type": "shell", "command": "npm run deploy:prod"},
            ],
            "edges": [
                {"from": "build", "to": "test"},
                {"from": "build", "to": "lint"},
                {"from": "test", "to": "deploy_staging"},
                {"from": "lint", "to": "deploy_staging"},
                {"from": "deploy_staging", "to": "approve"},
                {"from": "approve", "to": "deploy_prod"},
            ],
        },
        "version": 1,
        "tags": ["ci-cd", "production", "deploy"],
        "is_template": True,
        "project_id": uuid_str("erp"),
        "created_by": uuid_str("admin"),
    },
    {
        "id": uuid_str("code_review"),
        "name": "Code Review Automatizado",
        "description": "Review automático de código com IA",
        "definition": {
            "nodes": [
                {"id": "analyze", "type": "agent", "agent_type": "architect"},
                {"id": "security", "type": "agent", "agent_type": "security"},
                {"id": "performance", "type": "agent", "agent_type": "reviewer"},
                {"id": "report", "type": "python", "code": "generate_report(results)"},
            ],
            "edges": [
                {"from": "analyze", "to": "report"},
                {"from": "security", "to": "report"},
                {"from": "performance", "to": "report"},
            ],
        },
        "version": 1,
        "tags": ["code-review", "automation"],
        "is_template": True,
        "project_id": uuid_str("chatbot"),
        "created_by": uuid_str("dev"),
    },
]

# ── Provedores IA ─────────────────────────────────────────────────

PROVIDERS: list[dict[str, Any]] = [
    {
        "id": uuid_str("openai"),
        "name": "OpenAI",
        "type": "openai",
        "config": {"api_key_env": "OPENAI_API_KEY", "default_model": "gpt-4"},
        "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
        "is_default": True,
        "is_active": True,
        "priority": 1,
        "project_id": uuid_str("erp"),
        "created_by": uuid_str("admin"),
    },
    {
        "id": uuid_str("anthropic"),
        "name": "Anthropic",
        "type": "anthropic",
        "config": {"api_key_env": "ANTHROPIC_API_KEY", "default_model": "claude-3-sonnet"},
        "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
        "is_default": False,
        "is_active": True,
        "priority": 2,
        "project_id": uuid_str("erp"),
        "created_by": uuid_str("admin"),
    },
    {
        "id": uuid_str("ollama"),
        "name": "Ollama (Local)",
        "type": "ollama",
        "config": {"base_url": "http://localhost:11434", "default_model": "llama2"},
        "models": ["llama2", "codellama", "mistral"],
        "is_default": False,
        "is_active": True,
        "priority": 3,
        "project_id": uuid_str("chatbot"),
        "created_by": uuid_str("dev"),
    },
]

# ── Plugins ───────────────────────────────────────────────────────

PLUGINS: list[dict[str, Any]] = [
    {
        "id": uuid_str("git"),
        "slug": "git-integration",
        "name": "Git Integration",
        "version": "1.0.0",
        "description": "Integração completa com Git para versionamento",
        "manifest": {"author": "SuperDev Team", "permissions": ["filesystem:read", "terminal:execute"]},
        "status": "enabled",
        "config": {},
        "project_id": uuid_str("erp"),
        "installed_by": uuid_str("admin"),
    },
    {
        "id": uuid_str("docker"),
        "slug": "docker-manager",
        "name": "Docker Manager",
        "version": "1.0.0",
        "description": "Gerenciamento de containers Docker",
        "manifest": {"author": "SuperDev Team", "permissions": ["terminal:execute", "network:outbound"]},
        "status": "enabled",
        "config": {},
        "project_id": uuid_str("erp"),
        "installed_by": uuid_str("admin"),
    },
    {
        "id": uuid_str("database"),
        "slug": "database-tools",
        "name": "Database Tools",
        "version": "1.0.0",
        "description": "Ferramentas para gerenciamento de banco de dados",
        "manifest": {"author": "SuperDev Team", "permissions": ["database:read", "database:write"]},
        "status": "enabled",
        "config": {},
        "project_id": uuid_str("chatbot"),
        "installed_by": uuid_str("dev"),
    },
]


def get_all_seed_data() -> dict[str, list[dict[str, Any]]]:
    """Retorna todos os dados de seed organizados por tabela."""
    return {
        "users": USERS,
        "user_roles": USER_ROLES,
        "organizations": ORGANIZATIONS,
        "organization_members": ORGANIZATION_MEMBERS,
        "projects": PROJECTS,
        "project_members": PROJECT_MEMBERS,
        "agents": AGENTS,
        "workflows": WORKFLOWS,
        "providers": PROVIDERS,
        "plugins": PLUGINS,
    }


def seed_database(session: Any) -> None:
    """Popula o banco de dados com dados de exemplo.

    Idempotente: se ja existirem usuarios no banco, pula o seed.
    """
    from backend.database.models.agent import Agent
    from backend.database.models.organization import Organization, OrganizationMember
    from backend.database.models.plugin import Plugin
    from backend.database.models.project import Project, ProjectMember
    from backend.database.models.provider import Provider
    from backend.database.models.role import UserRole
    from backend.database.models.user import User
    from backend.database.models.workflow import Workflow
    from sqlalchemy import select

    # Verificar se ja existem dados
    existing = session.execute(select(User).limit(1)).scalar_one_or_none()
    if existing:
        print("[SKIP] Dados ja existem, pulando seed de dados")
        return

    data = get_all_seed_data()
    counts = {}

    # Inserir usuarios
    for row in data["users"]:
        session.add(User(**row))
    counts["users"] = len(data["users"])

    # Inserir organizacoes
    for row in data["organizations"]:
        session.add(Organization(**row))
    counts["organizations"] = len(data["organizations"])

    session.flush()

    # Inserir membros de organizacoes
    for row in data["organization_members"]:
        session.add(OrganizationMember(**row))
    counts["organization_members"] = len(data["organization_members"])

    # Inserir user_roles (associacao usuario -> role)
    for row in data["user_roles"]:
        session.add(UserRole(**row))
    counts["user_roles"] = len(data["user_roles"])

    # Inserir projetos
    for row in data["projects"]:
        session.add(Project(**row))
    counts["projects"] = len(data["projects"])

    session.flush()

    # Inserir membros de projetos
    for row in data["project_members"]:
        session.add(ProjectMember(**row))
    counts["project_members"] = len(data["project_members"])

    # Inserir agentes
    for row in data["agents"]:
        session.add(Agent(**row))
    counts["agents"] = len(data["agents"])

    # Inserir workflows
    for row in data["workflows"]:
        session.add(Workflow(**row))
    counts["workflows"] = len(data["workflows"])

    # Inserir provedores IA
    for row in data["providers"]:
        session.add(Provider(**row))
    counts["providers"] = len(data["providers"])

    # Inserir plugins
    for row in data["plugins"]:
        session.add(Plugin(**row))
    counts["plugins"] = len(data["plugins"])

    session.commit()

    parts = ", ".join(f"{k}: {v}" for k, v in counts.items())
    print(f"[OK] Seed concluido: {parts}")
