"""Custom agent DSL — define agents in YAML."""
from typing import Optional
import yaml


class AgentDSL:
    def __init__(self, raw: str):
        self.data = yaml.safe_load(raw)
        self.name: str = self.data.get("name", "unnamed")
        self.description: str = self.data.get("description", "")
        self.model: str = self.data.get("model", "gpt-4")
        self.tools: list = self.data.get("tools", [])
        self.system_prompt: Optional[str] = self.data.get("system_prompt")
        self.max_iterations: int = self.data.get("max_iterations", 10)
        self.memory: dict = self.data.get("memory", {"type": "short_term"})
        self.output_schema: Optional[dict] = self.data.get("output_schema")

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "model": self.model,
            "tools": self.tools,
            "system_prompt": self.system_prompt,
            "max_iterations": self.max_iterations,
            "memory": self.memory,
            "output_schema": self.output_schema,
        }

    @classmethod
    def from_file(cls, path: str) -> "AgentDSL":
        with open(path) as f:
            return cls(f.read())