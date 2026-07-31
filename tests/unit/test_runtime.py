"""Tests for runtime module: base_runtime, sandbox, runtime_manager."""

import pytest
from backend.runtime.base_runtime import (
    ExecutionResult,
    Language,
    ResourceLimits,
    RuntimeConfig,
    RuntimeStatus,
)
from backend.runtime.sandbox import SandboxManager


# ── Enums ───────────────────────────────────────────────────────────


class TestRuntimeEnums:
    def test_runtime_status_values(self):
        assert RuntimeStatus.PENDING.value == "pending"
        assert RuntimeStatus.RUNNING.value == "running"
        assert RuntimeStatus.COMPLETED.value == "completed"
        assert RuntimeStatus.FAILED.value == "failed"
        assert RuntimeStatus.TIMEOUT.value == "timeout"
        assert RuntimeStatus.CANCELLED.value == "cancelled"

    def test_language_values(self):
        assert Language.PYTHON.value == "python"
        assert Language.NODEJS.value == "nodejs"
        assert Language.GO.value == "go"
        assert Language.RUST.value == "rust"
        assert Language.SHELL.value == "shell"
        assert Language.BASH.value == "bash"


# ── ResourceLimits ──────────────────────────────────────────────────


class TestResourceLimits:
    def test_defaults(self):
        limits = ResourceLimits()
        assert limits.max_memory_mb == 512
        assert limits.max_cpu_percent == 50.0
        assert limits.max_execution_time_seconds == 300
        assert limits.max_output_size_bytes == 10 * 1024 * 1024
        assert limits.max_disk_mb == 1024

    def test_custom(self):
        limits = ResourceLimits(max_memory_mb=1024, max_cpu_percent=80.0)
        assert limits.max_memory_mb == 1024
        assert limits.max_cpu_percent == 80.0


# ── ExecutionResult ─────────────────────────────────────────────────


class TestExecutionResult:
    def test_defaults(self):
        result = ExecutionResult(run_id="r1", status=RuntimeStatus.COMPLETED)
        assert result.stdout == ""
        assert result.stderr == ""
        assert result.exit_code is None
        assert result.execution_time_ms == 0.0
        assert result.memory_used_mb == 0.0
        assert result.error is None
        assert result.artifacts == []

    def test_with_error(self):
        result = ExecutionResult(
            run_id="r1",
            status=RuntimeStatus.FAILED,
            error="Something failed",
            exit_code=1,
        )
        assert result.error == "Something failed"
        assert result.exit_code == 1


# ── RuntimeConfig ───────────────────────────────────────────────────


class TestRuntimeConfig:
    def test_minimal(self):
        config = RuntimeConfig(language=Language.PYTHON, code="print('hello')")
        assert config.filename is None
        assert config.entry_point is None
        assert config.dependencies == []
        assert config.env_vars == {}
        assert config.network_access is False

    def test_custom(self):
        config = RuntimeConfig(
            language=Language.NODEJS,
            code="console.log('hi')",
            filename="app.js",
            entry_point="app.js",
            dependencies=["lodash"],
            env_vars={"NODE_ENV": "test"},
            network_access=True,
        )
        assert config.filename == "app.js"
        assert config.network_access is True


# ── SandboxManager ──────────────────────────────────────────────────


class TestSandboxManager:
    def test_create_sandbox(self, tmp_path):
        mgr = SandboxManager(base_dir=str(tmp_path))
        path = mgr.create_sandbox("run1")
        assert path.exists()
        assert (path / "src").exists()
        assert (path / "output").exists()
        assert (path / "tmp").exists()

    def test_cleanup_sandbox(self, tmp_path):
        mgr = SandboxManager(base_dir=str(tmp_path))
        mgr.create_sandbox("run1")
        assert mgr.cleanup_sandbox("run1") is True
        assert mgr.get_sandbox_path("run1") is None

    def test_cleanup_nonexistent(self, tmp_path):
        mgr = SandboxManager(base_dir=str(tmp_path))
        assert mgr.cleanup_sandbox("nonexistent") is False

    def test_get_sandbox_path(self, tmp_path):
        mgr = SandboxManager(base_dir=str(tmp_path))
        mgr.create_sandbox("run1")
        assert mgr.get_sandbox_path("run1") is not None

    def test_get_sandbox_path_nonexistent(self, tmp_path):
        mgr = SandboxManager(base_dir=str(tmp_path))
        assert mgr.get_sandbox_path("nonexistent") is None

    def test_list_sandboxes(self, tmp_path):
        mgr = SandboxManager(base_dir=str(tmp_path))
        mgr.create_sandbox("run1")
        mgr.create_sandbox("run2")
        sandboxes = mgr.list_sandboxes()
        assert len(sandboxes) == 2
        assert "run1" in sandboxes
        assert "run2" in sandboxes

    def test_get_sandbox_size(self, tmp_path):
        mgr = SandboxManager(base_dir=str(tmp_path))
        path = mgr.create_sandbox("run1")
        (path / "test.txt").write_text("hello")
        size = mgr.get_sandbox_size("run1")
        assert size > 0

    def test_get_sandbox_size_nonexistent(self, tmp_path):
        mgr = SandboxManager(base_dir=str(tmp_path))
        assert mgr.get_sandbox_size("nonexistent") == 0

    @pytest.mark.asyncio
    async def test_write_and_read_file(self, tmp_path):
        mgr = SandboxManager(base_dir=str(tmp_path))
        mgr.create_sandbox("run1")
        await mgr.write_file("run1", "src/test.py", "print('hello')")
        content = await mgr.read_file("run1", "src/test.py")
        assert content == b"print('hello')"

    @pytest.mark.asyncio
    async def test_write_bytes(self, tmp_path):
        mgr = SandboxManager(base_dir=str(tmp_path))
        mgr.create_sandbox("run1")
        await mgr.write_file("run1", "data.bin", b"\x00\x01\x02")
        content = await mgr.read_file("run1", "data.bin")
        assert content == b"\x00\x01\x02"

    @pytest.mark.asyncio
    async def test_read_file_not_found(self, tmp_path):
        mgr = SandboxManager(base_dir=str(tmp_path))
        mgr.create_sandbox("run1")
        with pytest.raises(FileNotFoundError):
            await mgr.read_file("run1", "nonexistent.txt")

    def test_list_files(self, tmp_path):
        mgr = SandboxManager(base_dir=str(tmp_path))
        path = mgr.create_sandbox("run1")
        (path / "src" / "a.py").write_text("a")
        (path / "src" / "b.py").write_text("b")
        files = mgr.list_files("run1", "src")
        assert len(files) == 2
        names = [f["name"] for f in files]
        assert "a.py" in names
        assert "b.py" in names

    def test_list_files_nonexistent(self, tmp_path):
        mgr = SandboxManager(base_dir=str(tmp_path))
        assert mgr.list_files("nonexistent") == []


# ── RuntimeManager ──────────────────────────────────────────────────


class TestRuntimeManager:
    def test_detect_language_python(self):
        from backend.runtime.runtime_manager import RuntimeManager
        mgr = RuntimeManager()
        assert mgr.detect_language("app.py") == Language.PYTHON

    def test_detect_language_nodejs(self):
        from backend.runtime.runtime_manager import RuntimeManager
        mgr = RuntimeManager()
        assert mgr.detect_language("app.js") == Language.NODEJS
        assert mgr.detect_language("app.ts") == Language.NODEJS

    def test_detect_language_shell(self):
        from backend.runtime.runtime_manager import RuntimeManager
        mgr = RuntimeManager()
        assert mgr.detect_language("script.sh") == Language.SHELL
        assert mgr.detect_language("script.bash") == Language.SHELL

    def test_detect_language_unknown(self):
        from backend.runtime.runtime_manager import RuntimeManager
        mgr = RuntimeManager()
        assert mgr.detect_language("app.java") is None

    def test_get_runtime(self):
        from backend.runtime.runtime_manager import RuntimeManager
        mgr = RuntimeManager()
        assert mgr.get_runtime(Language.PYTHON) is not None
        assert mgr.get_runtime(Language.NODEJS) is not None
        assert mgr.get_runtime(Language.SHELL) is not None

    def test_get_runtime_unsupported(self):
        from backend.runtime.runtime_manager import RuntimeManager
        mgr = RuntimeManager()
        assert mgr.get_runtime(Language.GO) is None

    def test_register_runtime(self):
        from backend.runtime.runtime_manager import RuntimeManager
        from backend.runtime.base_runtime import BaseRuntime

        class DummyRuntime(BaseRuntime):
            @property
            def language(self):
                return Language.GO

            @property
            def supported_extensions(self):
                return [".go"]

            async def execute(self, config, run_id):
                return ExecutionResult(run_id=run_id, status=RuntimeStatus.COMPLETED)

            async def stream(self, config, run_id):
                yield "done"

        mgr = RuntimeManager()
        dummy = DummyRuntime()
        mgr.register_runtime(Language.GO, dummy)
        assert mgr.get_runtime(Language.GO) is dummy
