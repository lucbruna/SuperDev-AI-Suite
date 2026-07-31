"""Dataset builder for finetuning."""
from __future__ import annotations

import time
from typing import Any


class DatasetBuilder:
    def __init__(self) -> None:
        self._datasets: dict[str, dict[str, Any]] = {}
    def build(self, name: str, examples: list[dict[str, str]], template: str = "chat") -> dict[str, Any]:
        formatted = []
        for ex in examples:
            if template == "chat":
                formatted.append({"messages": [{"role": "user", "content": ex.get("input", "")}, {"role": "assistant", "content": ex.get("output", "")}]})
            else:
                formatted.append({"input": ex.get("input", ""), "output": ex.get("output", "")})
        ds = {"name": name, "data": formatted, "format": template, "created_at": time.time(), "size": len(formatted)}
        self._datasets[name] = ds
        return {"name": name, "size": len(formatted)}
    def merge(self, names: list[str], output_name: str) -> dict[str, Any]:
        merged = []
        for name in names:
            ds = self._datasets.get(name, {})
            merged.extend(ds.get("data", []))
        self._datasets[output_name] = {"name": output_name, "data": merged, "created_at": time.time(), "size": len(merged)}
        return {"name": output_name, "size": len(merged)}
    def split(self, name: str, train_ratio: float = 0.8) -> dict[str, Any]:
        ds = self._datasets.get(name, {})
        data = ds.get("data", [])
        split_point = int(len(data) * train_ratio)
        train_name = f"{name}_train"
        val_name = f"{name}_val"
        self._datasets[train_name] = {"name": train_name, "data": data[:split_point], "created_at": time.time(), "size": split_point}
        self._datasets[val_name] = {"name": val_name, "data": data[split_point:], "created_at": time.time(), "size": len(data) - split_point}
        return {"train": train_name, "val": val_name}
    def list_datasets(self) -> list[str]:
        return list(self._datasets.keys())
    def count(self, name: str) -> int:
        return len(self._datasets.get(name, {}).get("data", []))
