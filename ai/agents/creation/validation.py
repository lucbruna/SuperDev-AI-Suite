"""Validation utilities for agent creation."""
from __future__ import annotations

from typing import Any, Dict, List


VALID_AGENT_TYPES = {
    "supervisor", "planner", "coder", "security", "qa",
    "devops", "architect", "database", "frontend", "backend",
    "mobile", "monitoring", "documentation", "deployment",
    "testing", "research", "review", "custom",
}

VALID_CAPABILITIES = {
    "chat", "stream", "embeddings", "vision", "tools",
    "code_execution", "planning", "reasoning", "memory", "learning",
}

VALID_TIERS = {0, 1, 2, 3, 4}


class CreationValidator:
    """Validates agent configurations before creation."""

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        errors: List[str] = []
        if not config.get("name"):
            errors.append("name is required")
        if not config.get("agent_type") and not config.get("type"):
            errors.append("agent_type is required")
        agent_type = config.get("agent_type") or config.get("type", "")
        if agent_type and agent_type not in VALID_AGENT_TYPES:
            errors.append(f"Unknown agent_type: {agent_type}")
        tier = config.get("tier", 2)
        if tier not in VALID_TIERS:
            errors.append(f"Invalid tier: {tier}. Must be 0-4")
        return {"valid": len(errors) == 0, "errors": errors}

    def validate_tools(self, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        errors: List[str] = []
        for tool in tools:
            if not tool.get("name"):
                errors.append("Tool name is required")
        return {"valid": len(errors) == 0, "errors": errors}

    def validate_permissions(self, permissions: List[str]) -> Dict[str, Any]:
        errors: List[str] = []
        dangerous = {"sudo", "admin", "root", "execute_all"}
        for perm in permissions:
            if perm in dangerous:
                errors.append(f"Dangerous permission: {perm}")
        return {"valid": len(errors) == 0, "errors": errors}

    def validate_model(self, model_config: Dict[str, Any]) -> Dict[str, Any]:
        errors: List[str] = []
        provider = model_config.get("provider", "")
        if provider and provider not in {"openai", "anthropic", "gemini", "ollama", "openrouter"}:
            errors.append(f"Unknown provider: {provider}")
        temp = model_config.get("temperature", 0.7)
        if not 0.0 <= temp <= 2.0:
            errors.append(f"Temperature must be 0.0-2.0, got {temp}")
        return {"valid": len(errors) == 0, "errors": errors}

    def validate_capabilities(self, capabilities: List[str]) -> Dict[str, Any]:
        errors: List[str] = []
        for cap in capabilities:
            if cap not in VALID_CAPABILITIES:
                errors.append(f"Unknown capability: {cap}")
        return {"valid": len(errors) == 0, "errors": errors}

    def full_validation(self, config: Dict[str, Any]) -> Dict[str, Any]:
        all_errors: List[str] = []
        config_result = self.validate_config(config)
        all_errors.extend(config_result["errors"])
        tools = config.get("tools", [])
        if tools:
            tools_result = self.validate_tools(tools)
            all_errors.extend(tools_result["errors"])
        permissions = config.get("permissions", [])
        if permissions:
            perm_result = self.validate_permissions(permissions)
            all_errors.extend(perm_result["errors"])
        model = config.get("model", {})
        if model:
            model_result = self.validate_model(model)
            all_errors.extend(model_result["errors"])
        capabilities = config.get("capabilities", [])
        if capabilities:
            cap_result = self.validate_capabilities(capabilities)
            all_errors.extend(cap_result["errors"])
        return {"valid": len(all_errors) == 0, "errors": all_errors}
