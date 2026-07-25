from __future__ import annotations

import asyncio
import os
import tempfile
import time
from pathlib import Path

from backend.verification.models import ExecutionResult, VerificationStage


class CodeExecutor:
    def __init__(self, timeout: int = 60):
        self.timeout = timeout

    async def execute(
        self,
        code: str,
        language: str = "python",
        working_dir: str | None = None,
        env_vars: dict[str, str] | None = None,
    ) -> ExecutionResult:
        if language == "python":
            return await self._execute_python(code, working_dir, env_vars)
        elif language in ("javascript", "typescript"):
            return await self._execute_node(code, language, working_dir, env_vars)
        elif language == "bash":
            return await self._execute_bash(code, working_dir, env_vars)
        else:
            return ExecutionResult(
                success=False,
                error=f"Unsupported language: {language}",
                stage=VerificationStage.EXECUTE,
            )

    async def _execute_python(
        self,
        code: str,
        working_dir: str | None,
        env_vars: dict[str, str] | None,
    ) -> ExecutionResult:
        start = time.time()
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)

            process = await asyncio.create_subprocess_exec(
                "python",
                temp_file,
                cwd=working_dir,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout,
                )
            except TimeoutError:
                process.kill()
                await process.wait()
                return ExecutionResult(
                    success=False,
                    error=f"Execution timed out after {self.timeout}s",
                    execution_time=time.time() - start,
                    stage=VerificationStage.EXECUTE,
                )

            return ExecutionResult(
                success=process.returncode == 0,
                stdout=stdout.decode() if stdout else "",
                stderr=stderr.decode() if stderr else "",
                exit_code=process.returncode,
                execution_time=time.time() - start,
                stage=VerificationStage.EXECUTE,
            )
        finally:
            try:
                os.unlink(temp_file)
            except OSError:
                pass

    async def _execute_node(
        self,
        code: str,
        language: str,
        working_dir: str | None,
        env_vars: dict[str, str] | None,
    ) -> ExecutionResult:
        start = time.time()
        ext = ".js" if language == "javascript" else ".ts"
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=ext, delete=False) as f:
            if language == "typescript":
                f.write("// @ts-check\n")
            f.write(code)
            temp_file = f.name

        try:
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)

            cmd = ["node", temp_file] if language == "javascript" else ["tsx", temp_file]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=working_dir,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout,
                )
            except TimeoutError:
                process.kill()
                await process.wait()
                return ExecutionResult(
                    success=False,
                    error=f"Execution timed out after {self.timeout}s",
                    execution_time=time.time() - start,
                    stage=VerificationStage.EXECUTE,
                )

            return ExecutionResult(
                success=process.returncode == 0,
                stdout=stdout.decode() if stdout else "",
                stderr=stderr.decode() if stderr else "",
                exit_code=process.returncode,
                execution_time=time.time() - start,
                stage=VerificationStage.EXECUTE,
            )
        finally:
            try:
                os.unlink(temp_file)
            except OSError:
                pass

    async def _execute_bash(
        self,
        code: str,
        working_dir: str | None,
        env_vars: dict[str, str] | None,
    ) -> ExecutionResult:
        start = time.time()
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
            f.write("#!/bin/bash\n")
            f.write(code)
            temp_file = f.name

        try:
            os.chmod(temp_file, 0o755)
            
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)

            process = await asyncio.create_subprocess_exec(
                "bash",
                temp_file,
                cwd=working_dir,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout,
                )
            except TimeoutError:
                process.kill()
                await process.wait()
                return ExecutionResult(
                    success=False,
                    error=f"Execution timed out after {self.timeout}s",
                    execution_time=time.time() - start,
                    stage=VerificationStage.EXECUTE,
                )

            return ExecutionResult(
                success=process.returncode == 0,
                stdout=stdout.decode() if stdout else "",
                stderr=stderr.decode() if stderr else "",
                exit_code=process.returncode,
                execution_time=time.time() - start,
                stage=VerificationStage.EXECUTE,
            )
        finally:
            try:
                os.unlink(temp_file)
            except OSError:
                pass

    async def execute_in_project(
        self,
        files: dict[str, str],
        entry_point: str,
        language: str = "python",
        working_dir: str | None = None,
    ) -> ExecutionResult:
        if working_dir is None:
            working_dir = tempfile.mkdtemp()
        
        Path(working_dir).mkdir(parents=True, exist_ok=True)
        
        for filepath, content in files.items():
            full_path = Path(working_dir) / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        return await self.execute(
            code=f"# Running project\nimport sys\nsys.path.insert(0, '.')\nexec(open('{entry_point}').read())",
            language=language,
            working_dir=working_dir,
        )