"""Parameter manager for finetuning."""

from __future__ import annotations

from typing import Any


class ParameterManager:
    def __init__(self) -> None:
        self._configs: dict[str, dict[str, Any]] = {}

    def create_config(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        config = {"name": name, "params": params, "version": 1}
        self._configs[name] = config
        return config

    def get_config(self, name: str) -> dict[str, Any]:
        return self._configs.get(name, {"error": "not_found"})

    def update_config(self, name: str, params: dict[str, Any]) -> bool:
        if name not in self._configs:
            return False
        self._configs[name]["params"].update(params)
        self._configs[name]["version"] += 1
        return True

    def list_configs(self) -> list[str]:
        return list(self._configs.keys())

    def delete_config(self, name: str) -> bool:
        if name in self._configs:
            del self._configs[name]
            return True
        return False

    def preset_lora(self, rank: int = 8, alpha: int = 16, dropout: float = 0.1) -> dict[str, Any]:
        return {"method": "lora", "rank": rank, "alpha": alpha, "dropout": dropout}

    def preset_qlora(self, rank: int = 16, alpha: int = 32, bits: int = 4) -> dict[str, Any]:
        return {"method": "qlora", "rank": rank, "alpha": alpha, "bits": bits}

    def preset_prefix_tuning(self, num_virtual_tokens: int = 20) -> dict[str, Any]:
        return {"method": "prefix_tuning", "num_virtual_tokens": num_virtual_tokens}
