from __future__ import annotations

import os
from datetime import datetime
from typing import Any


class ProjectRules:
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self._rules_dir = os.path.join(project_root, ".superdev", "rules")

    def get_rules_path(self) -> str:
        paths = [
            os.path.join(self.project_root, ".superdevrules"),
            os.path.join(self.project_root, ".cursorrules"),
            os.path.join(self.project_root, ".superdev", "rules.yaml"),
            os.path.join(self.project_root, ".superdev", "rules.json"),
        ]
        for p in paths:
            if os.path.exists(p):
                return p
        return ""

    def load_rules(self) -> dict[str, Any]:
        path = self.get_rules_path()
        if not path:
            return {"rules": [], "path": None}
        with open(path, encoding="utf-8") as f:
            content = f.read()
        ext = os.path.splitext(path)[1]
        if ext in (".yaml", ".yml"):
            import yaml
            data = yaml.safe_load(content) or {}
        elif ext == ".json":
            import json
            data = json.loads(content)
        else:
            data = {"raw": content}
        return {"rules": data.get("rules", data.get("raw", content)), "path": path, "format": ext or "text"}

    def save_rules(self, rules: list[dict[str, Any]]) -> dict[str, Any]:
        os.makedirs(self._rules_dir, exist_ok=True)
        filepath = os.path.join(self._rules_dir, "rules.json")
        with open(filepath, "w", encoding="utf-8") as f:
            import json
            json.dump({"rules": rules, "updated_at": datetime.utcnow().isoformat(), "version": 2}, f, indent=2)
        return {"path": filepath, "count": len(rules)}

    def get_default_rules(self) -> list[dict[str, Any]]:
        return [
            {"id": "lang-python", "pattern": "*.py", "instruction": "Use type hints, follow PEP 8, max line length 120"},
            {"id": "lang-ts", "pattern": "*.ts", "instruction": "Use strict TypeScript, prefer interfaces over types"},
            {"id": "lang-tsx", "pattern": "*.tsx", "instruction": "Use React functional components with hooks"},
            {"id": "testing", "pattern": "test_*", "instruction": "Write tests first (TDD), aim for >80% coverage"},
            {"id": "security", "pattern": "*", "instruction": "Never hardcode secrets, validate all user input, use parameterized queries"},
            {"id": "docs", "pattern": "*.py", "instruction": "Write docstrings for all public functions and classes"},
        ]

    def apply_rules_to_prompt(self, rules: list[dict[str, Any]]) -> str:
        lines = ["## Project Rules\n"]
        for rule in rules:
            lines.append(f"- **{rule.get('pattern', '*')}**: {rule.get('instruction', '')}")
        return "\n".join(lines)
