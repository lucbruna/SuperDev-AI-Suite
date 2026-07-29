from __future__ import annotations

import os
from typing import Any

from ..base.base_agent import AgentResult, BaseAgent


class DocumentationAgent(BaseAgent):
    async def initialize(self) -> None:
        self._status = "ready"

    async def execute(self, task: str, context: dict[str, Any]) -> AgentResult:
        try:
            await self._check_cancelled()
            self._status = "running"

            path = context.get("path", task)
            files = self._collect_files(path)
            docs = self._generate_documentation(files, context)

            output_path = context.get("output_path", "README.md")
            if output_path:
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(docs)

            return AgentResult(
                success=True,
                output=docs,
                metrics={"files_processed": len(files), "output_file": output_path},
                artifacts={"documentation": docs, "files_processed": files},
            )
        except Exception as e:
            self._error_count += 1
            return AgentResult(success=False, output="", error=str(e))
        finally:
            self._status = "idle"

    def _collect_files(self, path: str) -> list[dict[str, str]]:
        files = []
        if not path or not os.path.exists(path):
            return files
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8") as f:
                    files.append({"path": path, "content": f.read()})
            except Exception:
                pass
        else:
            for root, _dirs, fnames in os.walk(path):
                for fname in fnames[:20]:
                    if fname.endswith((".py", ".js", ".ts", ".md", ".json", ".yaml", ".yml", ".toml")):
                        fpath = os.path.join(root, fname)
                        try:
                            with open(fpath, encoding="utf-8") as f:
                                files.append({"path": fpath, "content": f.read()})
                        except Exception:
                            pass
        return files

    def _generate_documentation(self, files: list[dict], context: dict) -> str:
        if not files:
            return "# Documentation\n\nNo files found to document."

        lines = ["# Project Documentation", "", "## Overview", context.get("description", "Auto-generated documentation."), ""]

        for f in files:
            lines.append(f"## File: {f['path']}")
            lines.append("")
            lines.append("### Contents")
            lines.append("")
            lines.append("```")
            content = f["content"][:1000]
            lines.append(content)
            if len(f["content"]) > 1000:
                lines.append("... (truncated)")
            lines.append("```")
            lines.append("")

        return "\n".join(lines)

    def capabilities(self) -> list[str]:
        return ["documentation_generation", "readme_creation", "code_documentation"]
