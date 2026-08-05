from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
import os
from pathlib import Path
import subprocess
from typing import Any
from urllib.parse import urlparse


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

    # Common parameter aliases that LLMs frequently produce instead of the
    # canonical names defined in tool schemas.  Normalising here keeps every
    # handler clean and avoids "unexpected keyword argument" failures.
    _PARAM_ALIASES: dict[str, dict[str, str]] = {
        "read_file":   {"file": "path", "file_path": "path", "filename": "path", "filepath": "path"},
        "write_file":  {"file": "path", "file_path": "path", "filename": "path", "filepath": "path"},
        "delete_file": {"file": "path", "file_path": "path", "filename": "path", "filepath": "path"},
        "list_files":  {"file": "path", "file_path": "path", "filename": "path", "filepath": "path"},
        "search_code": {"file_path": "path", "filepath": "path", "filename": "path", "query": "pattern"},
    }

    async def execute(self, name: str, **kwargs) -> Any:
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        aliases = self._PARAM_ALIASES.get(name, {})
        normalized = {aliases.get(k, k): v for k, v in kwargs.items()}
        return await tool.handler(**normalized)

    def delete(self, name: str) -> bool:
        if name in self._tools:
            del self._tools[name]
            return True
        return False


tool_registry = ToolRegistry()


def _workspace_root() -> Path:
    """Return the only directory that the coding agent may modify.

    ``SUPERDEV_WORKSPACE_ROOT`` makes the boundary explicit in deployments;
    falling back to the process directory keeps local development convenient.
    """
    return Path(os.environ.get("SUPERDEV_WORKSPACE_ROOT", Path.cwd())).resolve()


def _skills_root() -> Path:
    """Return the skills directory where agent skills are installed.

    This allows the agent to read skill instructions for enhanced workflows.
    """
    return Path.home() / ".agents" / "skills"


def _workspace_path(path: str, allow_skills: bool = False) -> Path:
    """Resolve *path* and reject paths that escape the allowed directories.

    By default, only the project workspace is allowed.
    When *allow_skills* is True, the skills directory is also permitted.
    """
    root = _workspace_root()
    candidate = Path(path)
    resolved = (candidate if candidate.is_absolute() else root / candidate).resolve()

    # Check workspace
    try:
        resolved.relative_to(root)
        return resolved
    except ValueError:
        pass

    # Check skills directory if allowed
    if allow_skills:
        skills = _skills_root()
        try:
            resolved.relative_to(skills)
            return resolved
        except ValueError:
            pass

    raise PermissionError("File operations are limited to the project workspace and skills directory")


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
    file_path = _workspace_path(path, allow_skills=True)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return file_path.read_text(encoding="utf-8")


async def _write_file(path: str, content: str) -> dict:
    file_path = _workspace_path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return {"path": str(file_path), "size": len(content)}


async def _list_files(path: str = ".") -> list[dict]:
    dir_path = _workspace_path(path, allow_skills=True)
    if not dir_path.exists():
        return []
    files = []
    for item in sorted(dir_path.iterdir()):
        files.append(
            {
                "name": item.name,
                "is_dir": item.is_dir(),
                "size": item.stat().st_size if item.is_file() else 0,
            }
        )
    return files


async def _search_code(pattern: str, path: str = ".") -> list[dict]:
    import re

    results = []
    dir_path = _workspace_path(path)
    regex = re.compile(pattern)

    for file in dir_path.rglob("*"):
        if len(results) >= 500:
            break
        if file.is_file() and file.suffix in (".py", ".js", ".ts", ".go", ".rs", ".java"):
            try:
                content = file.read_text(encoding="utf-8")
                for i, line in enumerate(content.splitlines(), 1):
                    if regex.search(line):
                        results.append(
                            {
                                "file": str(file),
                                "line": i,
                                "content": line.strip(),
                            }
                        )
            except Exception:
                continue
    return results


async def _delete_file(path: str) -> dict:
    """Remove one file or an empty directory from the project workspace."""
    file_path = _workspace_path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if file_path.is_dir():
        file_path.rmdir()
    else:
        file_path.unlink()
    return {"path": str(file_path), "deleted": True}


async def _clone_github_repository(url: str, destination: str, branch: str | None = None) -> dict:
    """Clone a GitHub repository into the project workspace."""
    parsed = urlparse(url)
    host = parsed.hostname or ""
    if parsed.scheme != "https" or host not in {"github.com", "www.github.com"}:
        raise ValueError("Only HTTPS GitHub repository URLs are supported")

    target = _workspace_path(destination)
    if target.exists() and any(target.iterdir()):
        raise FileExistsError(f"Destination is not empty: {destination}")
    if target.exists() and not target.is_dir():
        raise FileExistsError(f"Destination is a file: {destination}")
    target.parent.mkdir(parents=True, exist_ok=True)

    command = ["git", "clone", "--depth", "1"]
    if branch:
        command.extend(["--branch", branch])
    command.extend([url, str(target)])

    def clone() -> subprocess.CompletedProcess[str]:
        return subprocess.run(command, capture_output=True, text=True, timeout=180, check=False)

    result = await asyncio.to_thread(clone)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git clone failed")
    return {"repository": url, "path": str(target), "branch": branch, "cloned": True}


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
    name="delete_file",
    description="Delete a file or an empty directory in the project workspace",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to delete, relative to the workspace"},
        },
        "required": ["path"],
    },
    handler=_delete_file,
    tags=["file", "delete"],
)

tool_registry.register(
    name="clone_github_repository",
    description="Clone an HTTPS GitHub repository into a workspace directory",
    parameters={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "HTTPS URL of the GitHub repository"},
            "destination": {"type": "string", "description": "Empty destination directory, relative to workspace"},
            "branch": {"type": "string", "description": "Optional branch or tag to clone"},
        },
        "required": ["url", "destination"],
    },
    handler=_clone_github_repository,
    tags=["git", "network", "workspace"],
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


# ---------------------------------------------------------------------------
# Skills tools - allow agents to read and list installed skills
# ---------------------------------------------------------------------------


async def _list_skills() -> list[dict]:
    """List all installed agent skills."""
    skills_dir = _skills_root()
    if not skills_dir.exists():
        return []
    skills = []
    for item in sorted(skills_dir.iterdir()):
        if item.is_dir():
            skill_md = item / "SKILL.md"
            description = ""
            if skill_md.exists():
                try:
                    content = skill_md.read_text(encoding="utf-8")
                    # Extract description from frontmatter
                    for line in content.splitlines():
                        if line.startswith("description:"):
                            description = line.split(":", 1)[1].strip().strip('"').strip("'")
                            break
                except Exception:
                    pass
            skills.append({
                "name": item.name,
                "has_skill_md": skill_md.exists(),
                "description": description,
            })
    return skills


async def _read_skill(skill_name: str) -> str:
    """Read the SKILL.md file for a specific installed skill."""
    skills_dir = _skills_root()
    skill_path = skills_dir / skill_name / "SKILL.md"
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill not found: {skill_name}")
    return skill_path.read_text(encoding="utf-8")


tool_registry.register(
    name="list_skills",
    description="List all installed agent skills with their descriptions",
    parameters={
        "type": "object",
        "properties": {},
    },
    handler=_list_skills,
    tags=["skills", "list"],
)

tool_registry.register(
    name="read_skill",
    description="Read the SKILL.md instructions for a specific installed skill",
    parameters={
        "type": "object",
        "properties": {
            "skill_name": {"type": "string", "description": "Name of the skill to read"},
        },
        "required": ["skill_name"],
    },
    handler=_read_skill,
    tags=["skills", "read"],
)
