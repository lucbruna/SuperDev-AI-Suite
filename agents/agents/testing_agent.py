from __future__ import annotations

import asyncio
import os
import re
import sys
from typing import Any

from ..base.base_agent import AgentResult, BaseAgent


class TestingAgent(BaseAgent):
    async def initialize(self) -> None:
        self._status = "ready"

    async def execute(self, task: str, context: dict[str, Any]) -> AgentResult:
        try:
            await self._check_cancelled()
            self._status = "running"

            path = context.get("path", task)
            test_framework = context.get("framework", "pytest")
            test_dir = context.get("test_dir", "")

            test_files = self._generate_tests(path, context)
            created_files = []
            for test_file in test_files:
                filepath = self._write_test_file(test_file, test_dir)
                created_files.append(filepath)

            test_results = await self._run_tests(created_files, test_framework)

            report = self._build_report(created_files, test_results)

            return AgentResult(
                success=test_results.get("success", True),
                output=report,
                metrics={
                    "test_files_created": len(created_files),
                    "tests_passed": test_results.get("passed", 0),
                    "tests_failed": test_results.get("failed", 0),
                    "coverage": test_results.get("coverage", 0),
                },
                artifacts={
                    "test_files": created_files,
                    "results": test_results,
                },
            )
        except Exception as e:
            self._error_count += 1
            return AgentResult(success=False, output="", error=str(e))
        finally:
            self._status = "idle"

    def _generate_tests(self, path: str, context: dict) -> list[dict[str, str]]:
        test_files = []
        if not os.path.exists(path):
            return test_files

        files_to_test = []
        if os.path.isfile(path):
            files_to_test.append(path)
        else:
            for root, dirs, fnames in os.walk(path):
                for fname in fnames:
                    if fname.endswith(".py") and not fname.startswith("test_"):
                        files_to_test.append(os.path.join(root, fname))

        for fpath in files_to_test[:5]:
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()

                module_name = os.path.splitext(os.path.basename(fpath))[0]
                funcs = []
                for line in content.split("\n"):
                    if line.strip().startswith("def ") and "def __" not in line:
                        func_name = line.strip()[4:].split("(")[0]
                        funcs.append(func_name)

                funcs_list = ', '.join(funcs[:5]) if funcs else module_name
                test_content = [
                    f'"""Tests for {os.path.basename(fpath)}."""',
                    "import pytest",
                    f"from {module_name} import {funcs_list}",
                    "",
                ]
                for func in funcs[:5]:
                    test_content.extend([
                        "",
                        f"def test_{func}():",
                        f'    """Test {func} function."""',
                        f"    result = {func}()",
                        "    assert result is not None",
                        "",
                    ])

                test_files.append({
                    "path": fpath,
                    "test_content": "\n".join(test_content),
                    "module_name": module_name,
                })
            except Exception:
                pass

        return test_files

    def _write_test_file(self, test_file: dict, test_dir: str) -> str:
        if test_dir:
            os.makedirs(test_dir, exist_ok=True)
            filepath = os.path.join(test_dir, f"test_{os.path.basename(test_file['path'])}")
        else:
            fdir = os.path.dirname(test_file["path"])
            filepath = os.path.join(fdir, f"test_{os.path.basename(test_file['path'])}")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(test_file["test_content"])
        return filepath

    async def _run_tests(self, test_files: list[str], framework: str) -> dict[str, Any]:
        if not test_files:
            return {"success": True, "passed": 0, "failed": 0, "coverage": 0}

        test_dir = os.path.dirname(test_files[0])
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, "-m", framework,
                test_dir,
                "-v",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
            output = stdout.decode() if stdout else ""
            passed = len(re.findall(r"PASSED", output))
            failed = len(_re.findall(r"FAILED", output))
            return {
                "success": proc.returncode == 0,
                "passed": passed,
                "failed": failed,
                "coverage": 0,
                "output": output,
            }
        except Exception as e:
            return {"success": False, "passed": 0, "failed": 0, "coverage": 0, "error": str(e)}

    def _build_report(self, created_files: list, results: dict) -> str:
        lines = [
            "## Test Report",
            "",
            f"**Test files created:** {len(created_files)}",
        ]
        for f in created_files:
            lines.append(f"- {f}")
        lines.extend([
            "",
            "### Results",
            f"Passed: {results.get('passed', 0)}",
            f"Failed: {results.get('failed', 0)}",
        ])
        if results.get("output"):
            lines.extend(["", "### Output", "```", results["output"][:1000], "```"])
        return "\n".join(lines)

    def capabilities(self) -> list[str]:
        return ["test_generation", "pytest_execution", "test_analysis"]
