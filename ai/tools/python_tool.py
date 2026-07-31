from __future__ import annotations

import asyncio
import contextlib
import sys
import tempfile
from typing import Any


class PythonTool:
    _name = "python"
    _description = "Execute Python code in a subprocess"
    _permissions = ["execute"]

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "code" in params and isinstance(params["code"], str)

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        code = params.get("code", "")
        imports = params.get("imports", [])
        timeout = params.get("timeout", 30)

        if not code:
            return {"success": False, "stdout": "", "stderr": "No code provided", "exit_code": -1}

        full_code = "\n".join(imports) + "\n\n" + code if imports else code

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(full_code)
            script_path = f.name

        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            return {
                "success": proc.returncode == 0,
                "stdout": stdout.decode("utf-8", errors="replace") if stdout else "",
                "stderr": stderr.decode("utf-8", errors="replace") if stderr else "",
                "exit_code": proc.returncode or 0,
            }
        except TimeoutError:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Code execution timed out after {timeout}s",
                "exit_code": -1,
            }
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e), "exit_code": -1}
        finally:
            import os

            with contextlib.suppress(Exception):
                os.unlink(script_path)

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        pass
