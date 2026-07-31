"""SuperDev AI Suite - Backend Simplificado para demonstração."""

import hmac
import os
import secrets
import time
from contextlib import asynccontextmanager

# ── Health Monitor ────────────────────────────────────────────────
import psutil
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def get_system_stats():
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    return {
        "cpu_percent": cpu,
        "memory_percent": mem.percent,
        "memory_used_mb": mem.used // (1024**2),
        "disk_percent": disk.percent,
    }


# ── App Lifespan ──────────────────────────────────────────────────

start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 SuperDev AI Suite iniciado!")
    yield
    print("👋 SuperDev AI Suite encerrado!")


# ── Create App ────────────────────────────────────────────────────

app = FastAPI(
    title="SuperDev AI Suite",
    version="5.0.0",
    description="Plataforma de desenvolvimento impulsionada por IA",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# ── Routes ────────────────────────────────────────────────────────


@app.get("/")
async def root():
    return {
        "name": "SuperDev AI Suite",
        "version": "5.0.0",
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    stats = get_system_stats()
    return {
        "status": "healthy",
        "uptime_seconds": time.time() - start_time,
        "system": stats,
    }


@app.get("/api/v1/status")
async def status():
    return {
        "success": True,
        "data": {
            "version": "5.0.0",
            "name": "SuperDev AI Suite",
            "environment": "development",
            "uptime": time.time() - start_time,
        },
    }


# ── Agents ────────────────────────────────────────────────────────

agents_db = [
    {"id": "agent_001", "name": "Architect Agent", "type": "architect", "status": "idle"},
    {"id": "agent_002", "name": "Executor Agent", "type": "executor", "status": "idle"},
    {"id": "agent_003", "name": "Reviewer Agent", "type": "reviewer", "status": "idle"},
    {"id": "agent_004", "name": "Testing Agent", "type": "testing", "status": "idle"},
]


@app.get("/api/v1/agents")
async def list_agents():
    return {"success": True, "data": agents_db}


@app.get("/api/v1/agents/{agent_id}")
async def get_agent(agent_id: str):
    for agent in agents_db:
        if agent["id"] == agent_id:
            return {"success": True, "data": agent}
    return {"success": False, "error": "Agente não encontrado"}


@app.post("/api/v1/agents/{agent_id}/start")
async def start_agent(agent_id: str):
    for agent in agents_db:
        if agent["id"] == agent_id:
            agent["status"] = "running"
            return {"success": True, "data": agent}
    return {"success": False, "error": "Agente não encontrado"}


@app.post("/api/v1/agents/{agent_id}/stop")
async def stop_agent(agent_id: str):
    for agent in agents_db:
        if agent["id"] == agent_id:
            agent["status"] = "idle"
            return {"success": True, "data": agent}
    return {"success": False, "error": "Agente não encontrado"}


# ── Projects ──────────────────────────────────────────────────────

projects_db = [
    {"id": "proj_001", "name": "Sistema ERP", "status": "active", "description": "Sistema de gestão empresarial"},
    {"id": "proj_002", "name": "Chatbot IA", "status": "active", "description": "Chatbot inteligente"},
    {"id": "proj_003", "name": "API Gateway", "status": "draft", "description": "Gateway de APIs"},
]


@app.get("/api/v1/projects")
async def list_projects():
    return {"success": True, "data": projects_db}


@app.post("/api/v1/projects")
async def create_project(project: dict):
    new_project = {
        "id": f"proj_{len(projects_db) + 1:03d}",
        "name": project.get("name", "Novo Projeto"),
        "status": "active",
        "description": project.get("description", ""),
    }
    projects_db.append(new_project)
    return {"success": True, "data": new_project}


# ── Workflows ─────────────────────────────────────────────────────

workflows_db = [
    {"id": "wf_001", "name": "Deploy Pipeline", "status": "active", "version": 1},
    {"id": "wf_002", "name": "Code Review", "status": "active", "version": 1},
]


@app.get("/api/v1/workflows")
async def list_workflows():
    return {"success": True, "data": workflows_db}


# ── Providers ─────────────────────────────────────────────────────

providers_db = [
    {"id": "prov_001", "name": "OpenAI", "type": "openai", "status": "healthy"},
    {"id": "prov_002", "name": "Anthropic", "type": "anthropic", "status": "healthy"},
    {"id": "prov_003", "name": "Ollama", "type": "ollama", "status": "unknown"},
]


@app.get("/api/v1/providers")
async def list_providers():
    return {"success": True, "data": providers_db}


# ── Chat ──────────────────────────────────────────────────────────


@app.post("/api/v1/chat")
async def chat(message: dict):
    user_msg = message.get("message", "")
    return {
        "success": True,
        "data": {
            "message": f"Echo: {user_msg}",
            "model": "gpt-4",
            "provider": "openai",
        },
    }


# ── Plugins ───────────────────────────────────────────────────────

plugins_db = [
    {"id": "plug_001", "name": "Git Integration", "version": "1.0.0", "installed": True},
    {"id": "plug_002", "name": "Docker Manager", "version": "1.0.0", "installed": True},
    {"id": "plug_003", "name": "Database Tools", "version": "1.0.0", "installed": True},
]


@app.get("/api/v1/plugins")
async def list_plugins():
    return {"success": True, "data": plugins_db}


# ── Admin User (apenas para dev) ──────────────────────────────────
# ⚠️ Demo-only: os endpoints /users/me e /users não exigem autenticação real.

ADMIN_USER = {
    "id": "usr_admin_001",
    "email": os.getenv("ADMIN_EMAIL", "admin@superdev.com"),
    "name": "Administrador Master",
    "password": os.getenv("ADMIN_PASSWORD", "change-me-in-production"),
    "is_active": True,
    "is_superuser": True,
    "role": "admin",
    "permissions": [
        "users:create",
        "users:read",
        "users:update",
        "users:delete",
        "projects:create",
        "projects:read",
        "projects:update",
        "projects:delete",
        "agents:create",
        "agents:read",
        "agents:update",
        "agents:delete",
        "agents:execute",
        "workflows:create",
        "workflows:read",
        "workflows:update",
        "workflows:delete",
        "workflows:execute",
        "plugins:install",
        "plugins:uninstall",
        "plugins:configure",
        "providers:configure",
        "providers:enable",
        "providers:disable",
        "settings:read",
        "settings:update",
        "admin:full_access",
        "security:audit",
        "system:manage",
    ],
    "organizations": ["org_superdev_001"],
    "created_at": "2025-01-01T00:00:00Z",
}


# ── Auth (simplificado) ──────────────────────────────────────────


@app.post("/api/v1/auth/login")
async def login(credentials: dict):
    email = credentials.get("email", "")
    password = credentials.get("password", "")

    # Comparação em tempo constante + token aleatório (nunca estático).
    if email == ADMIN_USER["email"] and hmac.compare_digest(password, ADMIN_USER["password"]):
        return {
            "success": True,
            "data": {
                "access_token": secrets.token_urlsafe(32),
                "token_type": "Bearer",
                "expires_in": 86400,
                "user": {
                    "id": ADMIN_USER["id"],
                    "email": ADMIN_USER["email"],
                    "name": ADMIN_USER["name"],
                    "is_active": ADMIN_USER["is_active"],
                    "is_superuser": ADMIN_USER["is_superuser"],
                    "role": ADMIN_USER["role"],
                    "permissions": ADMIN_USER["permissions"],
                },
            },
        }

    # Credenciais inválidas
    return {"success": False, "error": "Email ou senha inválidos"}


@app.post("/api/v1/auth/register")
async def register(data: dict):
    name = data.get("name", "")
    email = data.get("email", "")
    password = data.get("password", "")

    if not all([name, email, password]):
        return {"success": False, "error": "Nome, email e senha são obrigatórios"}

    new_user = {
        "id": f"usr_{len(users_db) + 1:03d}",
        "name": name,
        "email": email,
        "is_active": True,
        "is_superuser": False,
        "role": "user",
        "permissions": ["projects:read", "projects:create"],
    }
    users_db.append(new_user)

    return {
        "success": True,
        "data": {
            "access_token": secrets.token_urlsafe(32),
            "user": new_user,
        },
    }


# ── Users ─────────────────────────────────────────────────────────

users_db = [ADMIN_USER]


@app.get("/api/v1/users/me")
async def get_current_user():
    return {
        "success": True,
        "data": {
            "id": ADMIN_USER["id"],
            "email": ADMIN_USER["email"],
            "name": ADMIN_USER["name"],
            "is_active": ADMIN_USER["is_active"],
            "is_superuser": ADMIN_USER["is_superuser"],
            "role": ADMIN_USER["role"],
            "permissions": ADMIN_USER["permissions"],
        },
    }


@app.get("/api/v1/users")
async def list_users():
    return {"success": True, "data": users_db}


@app.get("/api/v1/users/{user_id}")
async def get_user(user_id: str):
    for user in users_db:
        if user["id"] == user_id:
            return {"success": True, "data": user}
    return {"success": False, "error": "Usuário não encontrado"}


@app.delete("/api/v1/users/{user_id}")
async def delete_user(user_id: str):
    global users_db
    users_db = [u for u in users_db if u["id"] != user_id]
    return {"success": True, "message": "Usuário excluído"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
