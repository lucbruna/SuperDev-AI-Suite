"""Service-to-service authentication using API keys and JWT."""
import os
from functools import lru_cache

SERVICE_API_KEYS = {
    "backend": os.getenv("BACKEND_API_KEY", "dev-backend-key"),
    "ai_platform": os.getenv("AI_PLATFORM_API_KEY", "dev-ai-key"),
    "agents": os.getenv("AGENTS_API_KEY", "dev-agents-key"),
    "workflow_engine": os.getenv("WORKFLOW_API_KEY", "dev-workflow-key"),
    "runtime_engine": os.getenv("RUNTIME_API_KEY", "dev-runtime-key"),
}


def authenticate_service(service_name: str, api_key: str) -> bool:
    expected = SERVICE_API_KEYS.get(service_name)
    return expected is not None and expected == api_key


def get_service_token(service_name: str) -> str | None:
    return SERVICE_API_KEYS.get(service_name)


@lru_cache
def get_service_url(service_name: str) -> str:
    host_map = {
        "backend": "http://backend:8000",
        "ai_platform": "http://ai-platform:8001",
        "agents": "http://agents:8002",
        "workflow_engine": "http://workflow-engine:8003",
        "runtime_engine": "http://runtime-engine:8004",
    }
    return os.getenv(f"{service_name.upper()}_URL", host_map.get(service_name, ""))
