"""Creation configuration defaults and presets."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ModelDefaults:
    provider: str = "openai"
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 120


@dataclass
class SecurityPresets:
    sandbox_mode: bool = True
    allowed_tools: List[str] = field(default_factory=list)
    blocked_tools: List[str] = field(default_factory=lambda: ["shell", "filesystem_write"])
    max_tool_calls_per_step: int = 5
    require_approval: bool = False


@dataclass
class CapabilityPresets:
    chat: bool = True
    stream: bool = True
    tools: bool = False
    code_execution: bool = False
    vision: bool = False
    memory: bool = False
    planning: bool = False
    reasoning: bool = False
    learning: bool = False


# Per-type presets
AGENT_TYPE_PRESETS: Dict[str, Dict[str, Any]] = {
    "supervisor": {
        "model": ModelDefaults(temperature=0.3, max_tokens=8192),
        "capabilities": CapabilityPresets(
            chat=True, tools=True, planning=True, reasoning=True, memory=True,
        ),
        "security": SecurityPresets(require_approval=True),
    },
    "planner": {
        "model": ModelDefaults(temperature=0.4, max_tokens=6144),
        "capabilities": CapabilityPresets(planning=True, reasoning=True, memory=True),
        "security": SecurityPresets(),
    },
    "coder": {
        "model": ModelDefaults(temperature=0.2, max_tokens=4096),
        "capabilities": CapabilityPresets(
            chat=True, tools=True, code_execution=True,
        ),
        "security": SecurityPresets(sandbox_mode=True),
    },
    "security": {
        "model": ModelDefaults(temperature=0.1, max_tokens=4096),
        "capabilities": CapabilityPresets(reasoning=True, tools=True),
        "security": SecurityPresets(sandbox_mode=True),
    },
    "qa": {
        "model": ModelDefaults(temperature=0.2, max_tokens=4096),
        "capabilities": CapabilityPresets(
            chat=True, tools=True, code_execution=True,
        ),
        "security": SecurityPresets(),
    },
    "devops": {
        "model": ModelDefaults(temperature=0.2, max_tokens=4096),
        "capabilities": CapabilityPresets(chat=True, tools=True),
        "security": SecurityPresets(require_approval=True),
    },
    "architect": {
        "model": ModelDefaults(temperature=0.5, max_tokens=6144),
        "capabilities": CapabilityPresets(
            planning=True, reasoning=True, memory=True,
        ),
        "security": SecurityPresets(),
    },
}


class CreationConfiguration:
    """Global creation configuration with per-type defaults."""

    def __init__(self) -> None:
        self.model_defaults = ModelDefaults()
        self.security_presets = SecurityPresets()
        self.capability_presets = CapabilityPresets()
        self._type_presets = dict(AGENT_TYPE_PRESETS)

    def get_type_preset(self, agent_type: str) -> Dict[str, Any]:
        return self._type_presets.get(agent_type, {})

    def register_type_preset(self, agent_type: str, preset: Dict[str, Any]) -> None:
        self._type_presets[agent_type] = preset

    def list_type_presets(self) -> List[str]:
        return list(self._type_presets.keys())

    def snapshot(self) -> Dict[str, Any]:
        return {
            "type_presets": list(self._type_presets.keys()),
            "default_provider": self.model_defaults.provider,
        }
