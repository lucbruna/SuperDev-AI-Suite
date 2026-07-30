from __future__ import annotations

import asyncio
import json
import tempfile
import time
from pathlib import Path

from backend.verification.models import TestResult, VerificationStage


class CodeTester:
    def __init__(self, timeout: int = 120):
        self.timeout = timeout

    async def run_tests(
        self,
        code: str,
        language: str = "python",
        test_files: dict[str, str] | None = None,
        working_dir: str | None = None,
    ) -> TestResult:
        if language == "python":
            return await self._run_python_tests(code, test_files, working_dir)
        elif language in ("javascript", "typescript"):
            return await self._run_node_tests(code, test_files, working_dir)
        else:
            return TestResult(
                success=False,
                error=f"Unsupported language for testing: {language}",
                stage=VerificationStage.TEST,
            )

    async def _run_python_tests(
        self,
        code: str,
        test_files: dict[str, str] | None,
        working_dir: str | None,
    ) -> TestResult:
        start = time.time()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            src_dir = tmpdir_path / "src"
            src_dir.mkdir()
            
            (src_dir / "main.py").write_text(code)
            
            test_dir = tmpdir_path / "tests"
            test_dir.mkdir()
            
            if test_files:
                for name, content in test_files.items():
                    (test_dir / name).write_text(content)
            else:
                (test_dir / "test_main.py").write_text(self._generate_python_tests(code))

            env = {
                "PYTHONPATH": str(src_dir),
            }

            process = await asyncio.create_subprocess_exec(
                "python", "-m", "pytest", str(test_dir), "-v", "--tb=short", "--json-report",
                cwd=tmpdir,
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
                return TestResult(
                    success=False,
                    error=f"Tests timed out after {self.timeout}s",
                    execution_time=time.time() - start,
                    stage=VerificationStage.TEST,
                )

            output = stdout.decode(errors="replace") if stdout else ""
            error_output = stderr.decode(errors="replace") if stderr else ""
            
            result_file = test_dir / ".report.json"
            coverage = 0.0
            passed = 0
            failed = 0
            skipped = 0
            
            if result_file.exists():
                try:
                    report = json.loads(result_file.read_text())
                    summary = report.get("summary", {})
                    passed = summary.get("passed", 0)
                    failed = summary.get("failed", 0)
                    skipped = summary.get("skipped", 0)
                    
                    if "coverage" in report:
                        coverage = report["coverage"].get("total", {}).get("percent_covered", 0.0)
                except Exception:
                    pass

            total = passed + failed + skipped
            
            failures = []
            if failed > 0:
                for line in output.split("\n"):
                    if "FAILED" in line or "ERROR" in line:
                        failures.append({"test": line.strip(), "error": error_output})

            return TestResult(
                success=failed == 0,
                passed=passed,
                failed=failed,
                skipped=skipped,
                total=total,
                coverage=coverage,
                test_output=output,
                failures=failures,
                error=error_output if failed > 0 else None,
                execution_time=time.time() - start,
                stage=VerificationStage.TEST,
            )

    async def _run_node_tests(
        self,
        code: str,
        test_files: dict[str, str] | None,
        working_dir: str | None,
    ) -> TestResult:
        start = time.time()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            (tmpdir_path / "package.json").write_text(json.dumps({
                "name": "test-project",
                "version": "1.0.0",
                "scripts": {"test": "jest --json --outputFile=.report.json"},
                "devDependencies": {"jest": "^29.0.0", "ts-jest": "^29.0.0"},
            }))
            
            src_dir = tmpdir_path / "src"
            src_dir.mkdir()
            (src_dir / "index.js").write_text(code)
            
            test_dir = tmpdir_path / "tests"
            test_dir.mkdir()
            
            if test_files:
                for name, content in test_files.items():
                    (test_dir / name).write_text(content)
            else:
                (test_dir / "index.test.js").write_text(self._generate_js_tests(code))

            process = await asyncio.create_subprocess_exec(
                "npm", "install",
                cwd=tmpdir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await process.communicate()

            process = await asyncio.create_subprocess_exec(
                "npm", "test",
                cwd=tmpdir,
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
                return TestResult(
                    success=False,
                    error=f"Tests timed out after {self.timeout}s",
                    execution_time=time.time() - start,
                    stage=VerificationStage.TEST,
                )

            output = stdout.decode() if stdout else ""
            error_output = stderr.decode() if stderr else ""
            
            report_file = tmpdir_path / ".report.json"
            passed = 0
            failed = 0
            skipped = 0
            
            if report_file.exists():
                try:
                    report = json.loads(report_file.read_text())
                    for test_result in report.get("testResults", []):
                        for assertion in test_result.get("assertionResults", []):
                            if assertion["status"] == "passed":
                                passed += 1
                            elif assertion["status"] == "failed":
                                failed += 1
                            elif assertion["status"] == "skipped":
                                skipped += 1
                except Exception:
                    pass

            total = passed + failed + skipped
            
            failures = []
            if failed > 0:
                for line in output.split("\n"):
                    if "FAIL" in line or "✕" in line:
                        failures.append({"test": line.strip(), "error": error_output})

            return TestResult(
                success=failed == 0,
                passed=passed,
                failed=failed,
                skipped=skipped,
                total=total,
                test_output=output,
                failures=failures,
                error=error_output if failed > 0 else None,
                execution_time=time.time() - start,
                stage=VerificationStage.TEST,
            )

    def _generate_python_tests(self, code: str) -> str:
        return """import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Auto-generated tests
# TODO: Add specific test cases

def test_code_compiles():
    '''Test that the code compiles without syntax errors'''
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'main.py')) as f:
        code = f.read()
    compile(code, 'main.py', 'exec')

def test_basic_execution():
    '''Test basic execution of the module'''
    import main
    assert main is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""

    def _generate_js_tests(self, code: str) -> str:
        return """const fs = require('fs');
const path = require('path');

// Auto-generated tests
// TODO: Add specific test cases

describe('Generated Code', () => {
    test('code loads without errors', () => {
        expect(() => {
            require('../src/index.js');
        }).not.toThrow();
    });
});
"""