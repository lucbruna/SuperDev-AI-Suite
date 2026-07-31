from __future__ import annotations

import os
from typing import Any


class RenameRefactor:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run

    async def rename_symbol(
        self, filepath: str, old_name: str, new_name: str, language: str = "python"
    ) -> dict[str, Any]:
        if not os.path.exists(filepath):
            return {"success": False, "error": f"File not found: {filepath}"}
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        scope_patterns = {
            "python": f"\\b{old_name}\\b",
            "typescript": f"\\b{old_name}\\b",
            "javascript": f"\\b{old_name}\\b",
            "go": f"\\b{old_name}\\b",
            "rust": f"\\b{old_name}\\b",
        }
        import re

        pattern = scope_patterns.get(language, f"\\b{old_name}\\b")
        matches = list(re.finditer(pattern, content))
        if not matches:
            return {"success": False, "error": f"Symbol '{old_name}' not found in {filepath}", "occurrences": 0}
        new_content = re.sub(pattern, new_name, content)
        if not self.dry_run:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
        return {
            "success": True,
            "filepath": filepath,
            "old_name": old_name,
            "new_name": new_name,
            "occurrences": len(matches),
            "language": language,
            "dry_run": self.dry_run,
        }

    async def rename_file(self, old_path: str, new_path: str) -> dict[str, Any]:
        if not os.path.exists(old_path):
            return {"success": False, "error": f"File not found: {old_path}"}
        if os.path.exists(new_path):
            return {"success": False, "error": f"Target already exists: {new_path}"}
        if not self.dry_run:
            os.renames(old_path, new_path)
        return {"success": True, "from": old_path, "to": new_path, "dry_run": self.dry_run}

    async def batch_rename_symbol(
        self, files: list[str], old_name: str, new_name: str, language: str = "python"
    ) -> list[dict[str, Any]]:
        results = []
        for fp in files:
            result = await self.rename_symbol(fp, old_name, new_name, language)
            results.append(result)
        return results
