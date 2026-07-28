from __future__ import annotations

import difflib
from typing import Any


class PromptDiffer:
    @staticmethod
    def unified_diff(old_content: str, new_content: str, old_name: str = "old", new_name: str = "new") -> str:
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        return "".join(difflib.unified_diff(old_lines, new_lines, fromfile=old_name, tofile=new_name))

    @staticmethod
    def structured_diff(old_content: str, new_content: str) -> dict[str, Any]:
        old_lines = old_content.split("\n")
        new_lines = new_content.split("\n")
        changes = []
        matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue
            changes.append({
                "type": tag,
                "old_start": i1, "old_end": i2,
                "new_start": j1, "new_end": j2,
                "old_text": "\n".join(old_lines[i1:i2]) if tag in ("replace", "delete") else "",
                "new_text": "\n".join(new_lines[j1:j2]) if tag in ("replace", "insert") else "",
            })
        additions = sum(1 for c in changes if c["type"] in ("insert", "replace"))
        deletions = sum(1 for c in changes if c["type"] in ("delete", "replace"))
        return {
            "total_changes": len(changes),
            "additions": additions,
            "deletions": deletions,
            "changes": changes,
        }

    @staticmethod
    def semantic_diff(old_content: str, new_content: str) -> dict[str, Any]:
        sections = {
            "system_prompt_changed": False,
            "examples_changed": False,
            "formatting_changed": False,
            "constraints_changed": False,
        }
        old_lower = old_content.lower()
        new_lower = new_content.lower()
        if old_lower != new_lower:
            if "system" in old_lower or "system" in new_lower:
                sections["system_prompt_changed"] = old_content != new_content
            if "example" in old_lower or "example" in new_lower:
                sections["examples_changed"] = True
            if "format" in old_lower or "format" in new_lower:
                sections["formatting_changed"] = True
            if "constraint" in old_lower or "constraint" in new_lower:
                sections["constraints_changed"] = True
        return sections