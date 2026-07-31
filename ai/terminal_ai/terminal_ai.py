from __future__ import annotations

import os
import re
import shlex
import subprocess
from typing import Any

from pydantic_ai import Agent

TERMINAL_SYSTEM_PROMPT = """You are an AI terminal assistant for SuperDev. Given a user's natural language request or an error message, respond with:
1. A suggested shell command (if applicable) prefixed with `CMD:`
2. A plain-language explanation prefixed with `EXP:`

Only respond with these two prefixes. If no command is needed, omit CMD:."""

_agent = Agent(
    model=os.getenv("AI_MODEL", "openai:gpt-4o"),
    system_prompt=TERMINAL_SYSTEM_PROMPT,
)


def _parse_known_patterns(prompt: str) -> dict[str, Any] | None:
    prompt_lower = prompt.lower()

    patterns = {
        r"install\s+(\S+)": lambda m: {
            "command": f"pip install {m.group(1)}",
            "explanation": f"Installing {m.group(1)} package",
        },
        r"create\s+(?:a\s+)?agent\s+(\S+)": lambda m: {
            "command": f"superdev agent create --name {m.group(1)}",
            "explanation": f"Creating agent '{m.group(1)}'",
        },
        r"deploy\s+to\s+(\S+)": lambda m: {
            "command": f"superdev deploy --env {m.group(1)}",
            "explanation": f"Deploying to {m.group(1)} environment",
        },
        r"run\s+tests": lambda m: {"command": "superdev test run", "explanation": "Running all tests"},
        r"generate\s+docs": lambda m: {"command": "superdev docs generate", "explanation": "Generating documentation"},
        r"backup\s+(\S+)": lambda m: {
            "command": f"superdev backup create --name {m.group(1)}",
            "explanation": f"Creating backup '{m.group(1)}'",
        },
        r"cost\s+report": lambda m: {
            "command": "superdev cost report --period week",
            "explanation": "Generating weekly cost report",
        },
        r"audit\s+(\S+)": lambda m: {
            "command": f"superdev audit trail --days {m.group(1)}",
            "explanation": f"Audit trail for {m.group(1)} days",
        },
        r"git\s+commit": lambda m: {
            "command": 'git add . && git commit -m "update"',
            "explanation": "Staging and committing all changes",
        },
        r"list\s+agents": lambda m: {"command": "superdev agent list", "explanation": "Listing all agents"},
    }

    for pattern, handler in patterns.items():
        match = re.search(pattern, prompt_lower)
        if match:
            return handler(match)

    if "error" in prompt_lower or "failed" in prompt_lower:
        return {
            "explanation": "I detected an error context. Try running the command again with --verbose to get more details.",
            "command": None,
        }

    return None


async def handle_terminal_prompt(prompt: str) -> dict[str, Any]:
    known = _parse_known_patterns(prompt)
    if known:
        return known

    try:
        result = await _agent.run(prompt)
        text = result.data.strip()
        cmd = None
        exp = None
        for line in text.split("\n"):
            if line.startswith("CMD:"):
                cmd = line[4:].strip()
            elif line.startswith("EXP:"):
                exp = line[4:].strip()
        return {"command": cmd, "explanation": exp or text}
    except Exception as exc:
        return {"command": None, "explanation": f"AI unavailable: {exc}", "error": str(exc)}


def execute_command(command: str) -> dict[str, Any]:
    try:
        args = shlex.split(command)
        result = subprocess.run(args, capture_output=True, text=True, timeout=30)
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout[-2000:],
            "stderr": result.stderr[-2000:],
            "success": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {"exit_code": -1, "stdout": "", "stderr": "Command timed out after 30s", "success": False}
    except Exception as exc:
        return {"exit_code": -1, "stdout": "", "stderr": str(exc), "success": False}
