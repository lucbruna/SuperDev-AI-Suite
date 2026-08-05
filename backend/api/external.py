import uuid
from datetime import datetime

from fastapi import APIRouter

router = APIRouter(prefix="/api")


@router.post("/deploy/deploy")
async def deploy_app(env: str = "development", version: str = "latest", strategy: str = "rolling"):
    now = datetime.utcnow().isoformat()
    return {
        "id": f"dep_{uuid.uuid4().hex[:12]}",
        "env": env,
        "version": version,
        "strategy": strategy,
        "status": "running",
        "timestamp": now,
        "started_at": now,
    }


@router.post("/deploy/rollback")
async def rollback(env: str = "development"):
    return {"success": True, "env": env, "version": "previous", "strategy": "immediate", "status": "rolled_back"}


@router.get("/deploy/history")
async def deploy_history():
    return {"history": [], "total": 0}


@router.post("/code-review/run")
async def run_code_review(data: dict):
    return {
        "conclusion": "has_comments",
        "score": 72,
        "summary": f"Reviewed PR #{data.get('pr_number', '?')}. Found 2 issues.",
        "comments": [
            {"path": "src/main.py", "line": 42, "body": "Unused variable 'x'"},
            {"path": "src/utils.py", "line": 15, "body": "Consider adding type hints"},
        ],
        "total_issues": 2,
    }


@router.post("/evals/run")
async def run_eval(data: dict):
    return {
        "winner": "model_a",
        "prompts_count": len(data.get("prompts", [])),
        "summary": {
            "model_a": {"wins": 7, "avg_duration_ms": 1120},
            "model_b": {"wins": 3, "avg_duration_ms": 1450},
        },
    }


@router.get("/eval-harness/runs")
async def eval_harness_runs():
    return {"runs": [], "total": 0}


@router.post("/eval-harness/run")
async def eval_harness_run(model: str = "gpt-4"):
    return {
        "id": f"run_{uuid.uuid4().hex[:8]}",
        "model": model,
        "accuracy": 0.85,
        "results": [
            {"test": "test_math", "passed": True, "score": 0.9},
            {"test": "test_logic", "passed": True, "score": 0.8},
            {"test": "test_code_gen", "passed": False, "score": 0.4},
        ],
        "status": "completed",
    }


@router.post("/issue-to-pr/generate")
async def issue_to_pr_generate(data: dict):
    return {
        "id": f"pr_{uuid.uuid4().hex[:8]}",
        "title": f"Fix: {data.get('issue_description', 'issue')[:50]}",
        "description": "Automated PR generated from issue description.",
        "files_changed": ["src/fix.py"],
        "branch": f"fix/{uuid.uuid4().hex[:8]}",
        "status": "draft",
    }


@router.get("/configuration/rules")
async def get_rules():
    return {
        "rules": [
            {"id": "1", "name": "No console.log", "enabled": True, "pattern": "console\\.log"},
            {"id": "2", "name": "Use strict equality", "enabled": True, "pattern": "!=="},
        ]
    }


@router.put("/configuration/rules")
async def update_rules(data: dict):
    return {"success": True, "rules": data.get("rules", [])}


@router.get("/mcp/tools")
async def mcp_tools():
    return [
        {
            "name": "read_file",
            "description": "Read file contents",
            "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
        },
        {
            "name": "write_file",
            "description": "Write content to a file",
            "input_schema": {
                "type": "object",
                "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                "required": ["path", "content"],
            },
        },
        {
            "name": "execute_command",
            "description": "Run a shell command",
            "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
        },
    ]


@router.post("/terminal/ai")
async def terminal_ai(data: dict):
    prompt = data.get("prompt", "")
    return {
        "command": prompt,
        "explanation": f"Command suggestion for: '{prompt}'",
        "type": "command",
    }


# ------------------------------------------------------------------
# MCP tool execution
# ------------------------------------------------------------------

_MCP_TOOLS = [
    {
        "name": "read_file",
        "description": "Read file contents",
        "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
    },
    {
        "name": "write_file",
        "description": "Write content to a file",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"],
        },
    },
    {
        "name": "execute_command",
        "description": "Run a shell command",
        "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
    },
]


def _resolve_workspace_path(path: str) -> str:
    """Resolve a path relative to the workspace root, preventing escapes."""
    import os

    root = os.path.abspath(os.getcwd())
    candidate = os.path.abspath(os.path.join(root, path))
    if not (candidate == root or candidate.startswith(root + os.sep)):
        raise ValueError(f"Path escapes workspace root: {path}")
    return candidate


@router.post("/mcp/call")
async def mcp_call(data: dict):
    import asyncio
    import subprocess
    import time
    import uuid

    tool_name = data.get("tool_name", "")
    arguments = data.get("arguments") or {}
    tool_call_id = f"call_{uuid.uuid4().hex[:12]}"
    start = time.perf_counter()
    error: str | None = None
    result: dict | None = None

    try:
        if tool_name == "read_file":
            path = _resolve_workspace_path(str(arguments.get("path", "")))
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                result = {"content": f.read(), "path": path}
        elif tool_name == "write_file":
            path = _resolve_workspace_path(str(arguments.get("path", "")))
            with open(path, "w", encoding="utf-8") as f:
                f.write(str(arguments.get("content", "")))
            result = {"path": path, "written": True}
        elif tool_name == "execute_command":
            command = str(arguments.get("command", ""))
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=__import__("os").getcwd(),
            )
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
                result = {
                    "exit_code": proc.returncode,
                    "stdout": stdout.decode("utf-8", errors="replace")[:5000],
                    "stderr": stderr.decode("utf-8", errors="replace")[:2000],
                }
            except asyncio.TimeoutError:
                proc.kill()
                error = "Command timed out after 60s"
        else:
            error = f"Unknown tool: {tool_name}"
    except Exception as exc:  # noqa: BLE001
        error = str(exc)

    duration_ms = int((time.perf_counter() - start) * 1000)
    return {
        "tool_call_id": tool_call_id,
        "tool_name": tool_name,
        "result": result,
        "error": error,
        "duration_ms": duration_ms,
    }
