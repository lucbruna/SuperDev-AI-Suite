from __future__ import annotations

import os
from typing import Any


class SearchReplaceRefactor:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run

    async def execute(self, filepath: str, search: str, replace: str, count: int = 0) -> dict[str, Any]:
        if not os.path.exists(filepath):
            return {"success": False, "error": f"File not found: {filepath}"}
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        if count > 0:
            new_content = content.replace(search, replace, count)
            actual = content.count(search)
            occurrences = min(count, actual)
        else:
            new_content = content.replace(search, replace)
            occurrences = content.count(search)
        if new_content == content:
            return {"success": False, "error": f"Search string not found in {filepath}", "occurrences": 0}
        if not self.dry_run:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
        return {
            "success": True,
            "filepath": filepath,
            "occurrences": occurrences,
            "dry_run": self.dry_run,
            "chars_changed": abs(len(new_content) - len(content)),
        }

    async def multi_file(self, edits: list[dict[str, Any]]) -> list[dict[str, Any]]:
        results = []
        for edit in edits:
            result = await self.execute(edit["filepath"], edit["search"], edit["replace"], edit.get("count", 0))
            results.append(result)
        return results