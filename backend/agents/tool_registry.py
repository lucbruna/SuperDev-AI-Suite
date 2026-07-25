from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[..., Awaitable[Any]]
    tags: list[str] = field(default_factory=list)


class ToolRegistry:
    """Registry for agent tools."""

    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        handler: Callable[..., Awaitable[Any]],
        tags: list[str] | None = None,
    ) -> None:
        self._tools[name] = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler,
            tags=tags or [],
        )

    def get(self, name: str) -> ToolDefinition | None:
        return self._tools.get(name)

    def list_tools(self, tag: str | None = None) -> list[ToolDefinition]:
        tools = list(self._tools.values())
        if tag:
            tools = [t for t in tools if tag in t.tags]
        return tools

    def get_schemas(self) -> list[dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            }
            for tool in self._tools.values()
        ]

    async def execute(self, name: str, **kwargs) -> Any:
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        return await tool.handler(**kwargs)

    def delete(self, name: str) -> bool:
        if name in self._tools:
            del self._tools[name]
            return True
        return False


tool_registry = ToolRegistry()


async def _execute_code(code: str, language: str = "python") -> dict:
    from backend.runtime.base_runtime import Language, ResourceLimits, RuntimeConfig
    from backend.runtime.runtime_manager import runtime_manager
    from backend.utils.uuid_utils import generate_uuid

    lang = Language(language)
    config = RuntimeConfig(
        language=lang,
        code=code,
        resource_limits=ResourceLimits(max_execution_time_seconds=60),
    )
    result = await runtime_manager.execute(config, generate_uuid())
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.exit_code,
        "status": result.status.value,
    }


async def _read_file(path: str) -> str:
    from pathlib import Path
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return file_path.read_text(encoding="utf-8")


async def _write_file(path: str, content: str) -> dict:
    from pathlib import Path
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return {"path": str(file_path), "size": len(content)}


async def _list_files(path: str = ".") -> list[dict]:
    from pathlib import Path
    dir_path = Path(path)
    if not dir_path.exists():
        return []
    files = []
    for item in sorted(dir_path.iterdir()):
        files.append({
            "name": item.name,
            "is_dir": item.is_dir(),
            "size": item.stat().st_size if item.is_file() else 0,
        })
    return files


async def _search_code(pattern: str, path: str = ".") -> list[dict]:
    import re
    from pathlib import Path

    results = []
    dir_path = Path(path)
    regex = re.compile(pattern)

    for file in dir_path.rglob("*"):
        if file.is_file() and file.suffix in (".py", ".js", ".ts", ".go", ".rs", ".java"):
            try:
                content = file.read_text(encoding="utf-8")
                for i, line in enumerate(content.splitlines(), 1):
                    if regex.search(line):
                        results.append({
                            "file": str(file),
                            "line": i,
                            "content": line.strip(),
                        })
            except Exception:
                continue
    return results


tool_registry.register(
    name="execute_code",
    description="Execute code in a sandboxed environment",
    parameters={
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Code to execute"},
            "language": {"type": "string", "enum": ["python", "nodejs", "shell"], "default": "python"},
        },
        "required": ["code"],
    },
    handler=_execute_code,
    tags=["code", "execution"],
)

tool_registry.register(
    name="read_file",
    description="Read the contents of a file",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path to read"},
        },
        "required": ["path"],
    },
    handler=_read_file,
    tags=["file", "read"],
)

tool_registry.register(
    name="write_file",
    description="Write content to a file",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path to write"},
            "content": {"type": "string", "description": "Content to write"},
        },
        "required": ["path", "content"],
    },
    handler=_write_file,
    tags=["file", "write"],
)

tool_registry.register(
    name="list_files",
    description="List files in a directory",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Directory path", "default": "."},
        },
    },
    handler=_list_files,
    tags=["file", "list"],
)

tool_registry.register(
    name="search_code",
    description="Search for a pattern in code files",
    parameters={
        "type": "object",
        "properties": {
            "pattern": {"type": "string", "description": "Regex pattern to search for"},
            "path": {"type": "string", "description": "Directory path", "default": "."},
        },
        "required": ["pattern"],
    },
    handler=_search_code,
    tags=["code", "search"],
)
