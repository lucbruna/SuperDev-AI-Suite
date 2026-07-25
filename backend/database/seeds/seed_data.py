"""Seed data realista para o SuperDev."""

import uuid
from typing import Any


def generate_id() -> str:
    return str(uuid.uuid4())


# ── Usuários ──────────────────────────────────────────────────────

USERS = [
    {
        "id": "usr_admin_001",
        "email": "admin@superdev.com",
        "name": "Administrador",
        "hashed_password": "$2b$12$LJ3m4ys1Gz2YpH3rQ8J9KuYxZ5vW9tR4sA6dF7gH8jK0lM2nO3pQ",
        "is_active": True,
        "is_superuser": True,
        "language": "pt-BR",
        "timezone": "America/Sao_Paulo",
    },
    {
        "id": "usr_dev_001",
        "email": "dev@superdev.com",
        "name": "Desenvolvedor Principal",
        "hashed_password": "$2b$12$LJ3m4ys1Gz2YpH3rQ8J9KuYxZ5vW9tR4sA6dF7gH8jK0lM2nO3pQ",
        "is_active": True,
        "is_superuser": False,
        "language": "pt-BR",
        "timezone": "America/Sao_Paulo",
    },
    {
        "id": "usr_user_001",
        "email": "usuario@superdev.com",
        "name": "Usuário Padrão",
        "hashed_password": "$2b$12$LJ3m4ys1Gz2YpH3rQ8J9KuYxZ5vW9tR4sA6dF7gH8jK0lM2nO3pQ",
        "is_active": True,
        "is_superuser": False,
        "language": "en",
        "timezone": "America/New_York",
    },
]

# ── Organizações ──────────────────────────────────────────────────

ORGANIZATIONS = [
    {
        "id": "org_superdev_001",
        "name": "SuperDev Corp",
        "slug": "superdev-corp",
        "plan": "enterprise",
        "owner_id": "usr_admin_001",
    },
    {
        "id": "orgStartup_001",
        "name": "Startup Labs",
        "slug": "startup-labs",
        "plan": "pro",
        "owner_id": "usr_dev_001",
    },
]

# ── Projetos ──────────────────────────────────────────────────────

PROJECTS = [
    {
        "id": "proj_erp_001",
        "name": "Sistema ERP Completo",
        "description": "Sistema de gestão empresarial com módulos financeiro, estoque e RH",
        "status": "active",
        "organization_id": "org_superdev_001",
        "owner_id": "usr_admin_001",
        "template": "fastapi",
        "settings": {
            "language": "python",
            "framework": "fastapi",
            "database": "postgresql",
            "frontend": "react",
        },
    },
    {
        "id": "proj_chatbot_001",
        "name": "Chatbot Atendimento",
        "description": "Chatbot inteligente para atendimento ao cliente",
        "status": "active",
        "organization_id": "org_superdev_001",
        "owner_id": "usr_dev_001",
        "template": "fastapi",
        "settings": {
            "language": "python",
            "framework": "fastapi",
            "ai_provider": "openai",
            "model": "gpt-4",
        },
    },
    {
        "id": "proj_api_001",
        "name": "API Gateway",
        "description": "Gateway de APIs com rate limiting e autenticação",
        "status": "draft",
        "organization_id": "orgStartup_001",
        "owner_id": "usr_dev_001",
        "template": "node",
        "settings": {
            "language": "typescript",
            "framework": "express",
            "database": "redis",
        },
    },
]

# ── Agentes ───────────────────────────────────────────────────────

AGENTS = [
    {
        "id": "agent_architect_001",
        "name": "Architect Agent",
        "type": "architect",
        "status": "idle",
        "config": {
            "capabilities": ["architecture", "design_patterns", "code_review"],
            "model": "gpt-4",
            "max_tokens": 4096,
        },
        "project_id": "proj_erp_001",
    },
    {
        "id": "agent_executor_001",
        "name": "Executor Agent",
        "type": "executor",
        "status": "idle",
        "config": {
            "capabilities": ["code_generation", "refactoring", "debugging"],
            "model": "gpt-4",
            "max_tokens": 8192,
        },
        "project_id": "proj_erp_001",
    },
    {
        "id": "agent_reviewer_001",
        "name": "Reviewer Agent",
        "type": "reviewer",
        "status": "idle",
        "config": {
            "capabilities": ["code_review", "security_audit", "performance"],
            "model": "gpt-4",
            "max_tokens": 4096,
        },
        "project_id": "proj_chatbot_001",
    },
    {
        "id": "agent_tester_001",
        "name": "Testing Agent",
        "type": "testing",
        "status": "idle",
        "config": {
            "capabilities": ["unit_testing", "integration_testing", "e2e_testing"],
            "model": "gpt-4",
            "max_tokens": 4096,
        },
        "project_id": "proj_chatbot_001",
    },
]

# ── Workflows ─────────────────────────────────────────────────────

WORKFLOWS = [
    {
        "id": "wf_deploy_001",
        "name": "Pipeline de Deploy",
        "description": "Pipeline completo de CI/CD para produção",
        "status": "active",
        "version": 1,
        "graph": {
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
        "project_id": "proj_erp_001",
        "created_by": "usr_admin_001",
    },
    {
        "id": "wf_review_001",
        "name": "Code Review Automatizado",
        "description": "Review automático de código com IA",
        "status": "active",
        "version": 1,
        "graph": {
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
        "project_id": "proj_chatbot_001",
        "created_by": "usr_dev_001",
    },
]

# ── Provedores IA ─────────────────────────────────────────────────

PROVIDERS = [
    {
        "id": "provider_openai_001",
        "name": "OpenAI",
        "type": "openai",
        "is_enabled": True,
        "config": {
            "api_key_env": "OPENAI_API_KEY",
            "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "default_model": "gpt-4",
        },
        "health_status": "healthy",
    },
    {
        "id": "provider_anthropic_001",
        "name": "Anthropic",
        "type": "anthropic",
        "is_enabled": True,
        "config": {
            "api_key_env": "ANTHROPIC_API_KEY",
            "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
            "default_model": "claude-3-sonnet",
        },
        "health_status": "healthy",
    },
    {
        "id": "provider_ollama_001",
        "name": "Ollama (Local)",
        "type": "ollama",
        "is_enabled": True,
        "config": {
            "base_url": "http://localhost:11434",
            "models": ["llama2", "codellama", "mistral"],
            "default_model": "llama2",
        },
        "health_status": "unknown",
    },
]

# ── Plugins ───────────────────────────────────────────────────────

PLUGINS = [
    {
        "id": "plugin_git_001",
        "name": "Git Integration",
        "version": "1.0.0",
        "description": "Integração completa com Git para versionamento",
        "author": "SuperDev Team",
        "is_installed": True,
        "config": {},
        "permissions": ["filesystem:read", "terminal:execute"],
    },
    {
        "id": "plugin_docker_001",
        "name": "Docker Manager",
        "version": "1.0.0",
        "description": "Gerenciamento de containers Docker",
        "author": "SuperDev Team",
        "is_installed": True,
        "config": {},
        "permissions": ["terminal:execute", "network:outbound"],
    },
    {
        "id": "plugin_database_001",
        "name": "Database Tools",
        "version": "1.0.0",
        "description": "Ferramentas para gerenciamento de banco de dados",
        "author": "SuperDev Team",
        "is_installed": True,
        "config": {},
        "permissions": ["database:read", "database:write"],
    },
]

# ── Conversas ─────────────────────────────────────────────────────

CONVERSATIONS = [
    {
        "id": "conv_001",
        "title": "Arquitetura do ERP",
        "user_id": "usr_admin_001",
        "provider": "openai",
        "model": "gpt-4",
    },
    {
        "id": "conv_002",
        "title": "Debug do Chatbot",
        "user_id": "usr_dev_001",
        "provider": "anthropic",
        "model": "claude-3-sonnet",
    },
]

# ── Mensagens ─────────────────────────────────────────────────────

MESSAGES = [
    {
        "id": "msg_001",
        "conversation_id": "conv_001",
        "role": "user",
        "content": "Preciso projetar a arquitetura de um sistema ERP completo. Quais módulos devo incluir?",
        "model": "gpt-4",
        "tokens_used": 50,
    },
    {
        "id": "msg_002",
        "conversation_id": "conv_001",
        "role": "assistant",
        "content": "Para um ERP completo, recomendo os seguintes módulos:\n\n1. **Financeiro** - Contas a pagar/receber, fluxo de caixa\n2. **Estoque** - Gestão de produtos, entradas/saídas\n3. **RH** - Funcionários, folha de pagamento\n4. **Vendas** - CRM, pedidos, orçamentos\n5. **Compras** - Cotações, pedidos de compra\n6. **Produção** - Ordens de produção, planejamento\n7. **Relatórios** - Dashboards e indicadores",
        "model": "gpt-4",
        "tokens_used": 150,
    },
    {
        "id": "msg_003",
        "conversation_id": "conv_002",
        "role": "user",
        "content": "Meu chatbot está retornando erro 429. Como resolver?",
        "model": "claude-3-sonnet",
        "tokens_used": 30,
    },
    {
        "id": "msg_004",
        "conversation_id": "conv_002",
        "role": "assistant",
        "content": "O erro 429 indica rate limiting. Soluções:\n\n1. Implementar retry com backoff exponencial\n2. Adicionar cache de respostas\n3. Usar fila de mensagens\n4. Verificar limites do provedor",
        "model": "claude-3-sonnet",
        "tokens_used": 80,
    },
]


def get_all_seed_data() -> dict[str, list[dict[str, Any]]]:
    """Retorna todos os dados de seed organizados por tabela."""
    return {
        "users": USERS,
        "organizations": ORGANIZATIONS,
        "projects": PROJECTS,
        "agents": AGENTS,
        "workflows": WORKFLOWS,
        "providers": PROVIDERS,
        "plugins": PLUGINS,
        "conversations": CONVERSATIONS,
        "messages": MESSAGES,
    }


def seed_database(session: Any) -> None:
    """Popula o banco de dados com dados de exemplo."""
    from backend.database.models.organization import Organization
    from backend.database.models.project import Project
    from backend.database.models.user import User

    data = get_all_seed_data()

    # Inserir usuários
    for user_data in data["users"]:
        user = User(**user_data)
        session.add(user)

    # Inserir organizações
    for org_data in data["organizations"]:
        org = Organization(**org_data)
        session.add(org)

    # Inserir projetos
    for project_data in data["projects"]:
        project = Project(**project_data)
        session.add(project)

    session.commit()
    print(f"Seed concluído: {len(data['users'])} usuários, {len(data['organizations'])} orgs, {len(data['projects'])} projetos")
