from fastapi import APIRouter

router = APIRouter()

from backend.api.v1 import (
    admin,
    agents,
    api_keys,
    auth,
    builders,
    chat,
    cost,
    dashboard,
    executions,
    feature_flags,
    health,
    harness,
    knowledge,
    llm,
    organizations,
    plugins,
    projects,
    runtime,
    scanners,
    settings,
    system,
    users,
    verification,
    workflow,
)

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(health.router, tags=["health"])
v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])
v1_router.include_router(api_keys.router, prefix="/api-keys", tags=["api-keys"])
v1_router.include_router(users.router, prefix="/users", tags=["users"])
v1_router.include_router(projects.router, prefix="/projects", tags=["projects"])
v1_router.include_router(agents.router, prefix="/agents", tags=["agents"])
v1_router.include_router(chat.router, prefix="/chat", tags=["chat"])
v1_router.include_router(llm.router, prefix="/llm", tags=["llm"])
v1_router.include_router(runtime.router, prefix="/runtime", tags=["runtime"])
v1_router.include_router(workflow.router, prefix="/workflows", tags=["workflows"])
v1_router.include_router(plugins.router, prefix="/plugins", tags=["plugins"])
v1_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
v1_router.include_router(verification.router, prefix="/verify", tags=["verification"])
v1_router.include_router(admin.router, prefix="/admin", tags=["admin"])
v1_router.include_router(scanners.router, prefix="/scanners", tags=["scanners"])
v1_router.include_router(builders.router, prefix="/builders", tags=["builders"])
v1_router.include_router(settings.router, prefix="/settings", tags=["settings"])
v1_router.include_router(system.router, prefix="/system", tags=["system"])
v1_router.include_router(
    dashboard.router, prefix="/system", tags=["dashboard"]
)
v1_router.include_router(
    feature_flags.router, prefix="/feature-flags", tags=["feature-flags"]
)
v1_router.include_router(executions.router, prefix="/executions", tags=["executions"])
v1_router.include_router(cost.router, prefix="/cost", tags=["cost"])
v1_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
v1_router.include_router(harness.router, prefix="/harness", tags=["harness"])

router.include_router(v1_router)
