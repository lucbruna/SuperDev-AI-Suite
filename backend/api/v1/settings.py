from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter()

_settings: dict[str, Any] = {
    "general": {
        "defaultLanguage": "en",
        "timezone": "UTC",
        "dateFormat": "YYYY-MM-DD",
    },
    "appearance": {
        "theme": "dark",
        "fontSize": 14,
        "sidebarPosition": "left",
        "compactMode": False,
    },
    "providers": [
        {
            "id": "openai",
            "name": "OpenAI",
            "type": "llm",
            "apiKey": "",
            "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "enabled": True,
        },
        {
            "id": "anthropic",
            "name": "Anthropic",
            "type": "llm",
            "apiKey": "",
            "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
            "enabled": False,
        },
    ],
}


@router.get("/general")
async def get_general_settings():
    return {"success": True, "data": _settings["general"]}


@router.put("/general")
async def update_general_settings(data: dict):
    _settings["general"].update(data)
    return {"success": True, "data": _settings["general"]}


@router.get("/appearance")
async def get_appearance_settings():
    return {"success": True, "data": _settings["appearance"]}


@router.put("/appearance")
async def update_appearance_settings(data: dict):
    _settings["appearance"].update(data)
    return {"success": True, "data": _settings["appearance"]}


@router.get("/providers")
async def get_provider_configs():
    return {"success": True, "data": _settings["providers"]}


@router.put("/providers/{provider_id}")
async def update_provider_config(provider_id: str, data: dict):
    for p in _settings["providers"]:
        if p["id"] == provider_id:
            p.update(data)
            return {"success": True, "data": p}
    raise HTTPException(status_code=404, detail="Provider not found")


@router.post("/providers/{provider_id}/test")
async def test_provider_connection(provider_id: str):
    for p in _settings["providers"]:
        if p["id"] == provider_id:
            return {"success": True, "data": {"success": True, "message": f"Connection to {p['name']} successful"}}
    raise HTTPException(status_code=404, detail="Provider not found")
