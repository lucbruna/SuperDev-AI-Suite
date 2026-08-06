"""Tests for the Autonomous Developer config package (Phase A)."""
from __future__ import annotations

from modules.autonomous_developer import __version__
from modules.autonomous_developer.config import (
    CodingRules,
    DeveloperConfig,
    GeneratorConfig,
    LLMConfig,
    PlannerConfig,
    QualityRules,
    SecurityRules,
    StyleRules,
    allowed_operations,
    check_permission,
    contains_secret,
    get_default_config,
    redact_secrets,
    require_role,
)


class TestModuleVersion:
    def test_version_importable(self) -> None:
        assert isinstance(__version__, str)
        assert __version__

    def test_default_config_resolves(self, tmp_path) -> None:
        config = get_default_config()
        assert config.project_root
        assert config.data_dir
        config2 = DeveloperConfig()
        config2.resolve(str(tmp_path))
        assert config2.project_root == str(tmp_path.resolve())
        assert str(tmp_path.resolve()) in config2.data_dir


class TestDeveloperConfig:
    def test_defaults(self) -> None:
        cfg = DeveloperConfig()
        assert cfg.mode == "supervised"
        assert cfg.work_branch == "autonomous-dev"
        assert cfg.allow_main_branch_writes is False
        assert cfg.max_retries_per_task == 3
        assert cfg.run_tests is True
        assert cfg.create_pr is True

    def test_from_env_overrides(self, monkeypatch) -> None:
        monkeypatch.setenv("SUPERDEV_AD_MODE", "autonomous")
        monkeypatch.setenv("SUPERDEV_AD_WORK_BRANCH", "feature-branch")
        monkeypatch.setenv("SUPERDEV_AD_ALLOW_MAIN_WRITES", "true")
        monkeypatch.setenv("SUPERDEV_AD_RUN_TESTS", "false")
        cfg = DeveloperConfig.from_env()
        assert cfg.mode == "autonomous"
        assert cfg.work_branch == "feature-branch"
        assert cfg.allow_main_branch_writes is True
        assert cfg.run_tests is False

    def test_nested_configs_built(self) -> None:
        cfg = DeveloperConfig()
        assert isinstance(cfg.planner, PlannerConfig)
        assert isinstance(cfg.generator, GeneratorConfig)
        assert isinstance(cfg.llm, LLMConfig)

    def test_from_env_populates_nested(self, monkeypatch) -> None:
        monkeypatch.setenv("SUPERDEV_AD_PLANNER_MAX_TASKS", "7")
        monkeypatch.setenv("SUPERDEV_AD_LLM_ENABLED", "1")
        cfg = DeveloperConfig.from_env()
        assert cfg.planner.max_tasks_per_request == 7
        assert cfg.llm.enabled is True


class TestPlannerConfig:
    def test_defaults(self) -> None:
        cfg = PlannerConfig()
        assert cfg.decompose_tasks is True
        assert cfg.max_tasks_per_request == 20
        assert cfg.require_impact_analysis is True
        assert cfg.default_priority == "medium"

    def test_from_env(self, monkeypatch) -> None:
        monkeypatch.setenv("SUPERDEV_AD_PLANNER_DECOMPOSE", "false")
        monkeypatch.setenv("SUPERDEV_AD_PLANNER_MAX_TASKS", "5")
        cfg = PlannerConfig.from_env()
        assert cfg.decompose_tasks is False
        assert cfg.max_tasks_per_request == 5

    def test_bad_int_falls_back(self, monkeypatch) -> None:
        monkeypatch.setenv("SUPERDEV_AD_PLANNER_MAX_TASKS", "not-a-number")
        cfg = PlannerConfig.from_env()
        assert cfg.max_tasks_per_request == 20


class TestGeneratorConfig:
    def test_defaults(self) -> None:
        cfg = GeneratorConfig()
        assert cfg.max_files_per_task == 50
        assert cfg.allow_delete is False
        assert cfg.create_backups is True
        assert cfg.atomic_writes is True
        assert cfg.line_length == 100

    def test_from_env(self, monkeypatch) -> None:
        monkeypatch.setenv("SUPERDEV_AD_GENERATOR_ALLOW_DELETE", "yes")
        monkeypatch.setenv("SUPERDEV_AD_GENERATOR_MAX_FILES", "3")
        cfg = GeneratorConfig.from_env()
        assert cfg.allow_delete is True
        assert cfg.max_files_per_task == 3


class TestLLMConfig:
    def test_defaults(self) -> None:
        cfg = LLMConfig()
        assert cfg.enabled is False
        assert cfg.provider == "ollama"
        assert cfg.fallback_to_echo is True
        assert cfg.max_tokens == 4096

    def test_from_env(self, monkeypatch) -> None:
        monkeypatch.setenv("SUPERDEV_AD_LLM_ENABLED", "true")
        monkeypatch.setenv("SUPERDEV_AD_LLM_PROVIDER", "openai")
        monkeypatch.setenv("SUPERDEV_AD_LLM_TEMPERATURE", "0.7")
        cfg = LLMConfig.from_env()
        assert cfg.enabled is True
        assert cfg.provider == "openai"
        assert cfg.temperature == 0.7

    def test_temperature_env_defaults(self, monkeypatch) -> None:
        monkeypatch.setenv("SUPERDEV_AD_LLM_TEMPERATURE", "garbage")
        cfg = LLMConfig.from_env()
        assert cfg.temperature == 0.2


class TestCodingRules:
    def test_defaults(self) -> None:
        cfg = CodingRules()
        assert cfg.max_function_lines == 60
        assert cfg.max_function_parameters == 6
        assert cfg.max_cyclomatic_complexity == 10
        assert cfg.require_docstrings is True
        assert cfg.forbid_bare_excepts is True

    def test_from_env(self, monkeypatch) -> None:
        monkeypatch.setenv("SUPERDEV_AD_RULES_COMPLEXITY", "15")
        monkeypatch.setenv("SUPERDEV_AD_RULES_DOCSTRINGS", "false")
        cfg = CodingRules.from_env()
        assert cfg.max_cyclomatic_complexity == 15
        assert cfg.require_docstrings is False


class TestSecurityRules:
    def test_defaults_are_restrictive(self) -> None:
        cfg = SecurityRules()
        assert cfg.allow_shell_execution is False
        assert cfg.allow_network_access is False
        assert cfg.allow_secret_writes is False
        assert cfg.forbid_subprocess_with_shell is True

    def test_path_allowed_inside_project(self, tmp_path) -> None:
        cfg = SecurityRules()
        inside = tmp_path / "src" / "app.py"
        inside.parent.mkdir(parents=True)
        inside.write_text("x")
        assert cfg.is_path_allowed(inside, tmp_path) is True

    def test_path_blocked_outside_project(self, tmp_path) -> None:
        cfg = SecurityRules()
        outside = tmp_path.parent / "elsewhere.txt"
        assert cfg.is_path_allowed(outside, tmp_path) is False

    def test_blocked_pattern_rejected(self, tmp_path) -> None:
        cfg = SecurityRules()
        env_file = tmp_path / ".env"
        env_file.write_text("x")
        assert cfg.is_path_allowed(env_file, tmp_path) is False

    def test_allowed_paths_override_root(self, tmp_path) -> None:
        alt = tmp_path / "alt"
        alt.mkdir()
        cfg = SecurityRules(allowed_paths=(str(alt),))
        assert cfg.is_path_allowed(alt / "f.txt", tmp_path) is True
        assert cfg.is_path_allowed(tmp_path / "f.txt", tmp_path) is False

    def test_from_env_allowed_paths(self, monkeypatch, tmp_path) -> None:
        monkeypatch.setenv("SUPERDEV_AD_SECURITY_SHELL", "true")
        monkeypatch.setenv("SUPERDEV_AD_SECURITY_ALLOWED_PATHS", str(tmp_path))
        cfg = SecurityRules.from_env()
        assert cfg.allow_shell_execution is True
        assert cfg.allowed_paths == (str(tmp_path),)

    def test_contains_secret(self) -> None:
        assert contains_secret("password = 'hunter2'") is True
        assert contains_secret("api_key: sk-1234") is True
        assert contains_secret("-----BEGIN RSA PRIVATE KEY-----") is True
        assert contains_secret("def add(a, b): return a + b") is False

    def test_redact_secrets(self) -> None:
        out = redact_secrets("token=abc12345678901234567890123456789012")
        assert "[REDACTED]" in out
        assert "abc12345678901234567890123456789012" not in out


class TestQualityRules:
    def test_defaults(self) -> None:
        cfg = QualityRules()
        assert cfg.require_tests is True
        assert cfg.min_test_coverage == 0.80
        assert cfg.require_review is True
        assert cfg.required_reviewers == 1

    def test_from_env(self, monkeypatch) -> None:
        monkeypatch.setenv("SUPERDEV_AD_QUALITY_COVERAGE", "0.9")
        monkeypatch.setenv("SUPERDEV_AD_QUALITY_REQUIRE_REVIEW", "false")
        cfg = QualityRules.from_env()
        assert cfg.min_test_coverage == 0.9
        assert cfg.require_review is False


class TestStyleRules:
    def test_defaults(self) -> None:
        cfg = StyleRules()
        assert cfg.indent == 4
        assert cfg.max_line_length == 100
        assert cfg.quote_style == "double"
        assert cfg.name_conventions["class"] == "PascalCase"

    def test_from_env(self, monkeypatch) -> None:
        monkeypatch.setenv("SUPERDEV_AD_STYLE_INDENT", "2")
        monkeypatch.setenv("SUPERDEV_AD_STYLE_QUOTES", "single")
        cfg = StyleRules.from_env()
        assert cfg.indent == 2
        assert cfg.quote_style == "single"


class TestPermissions:
    def test_viewer_read_only(self) -> None:
        assert require_role("viewer", "task.read") is True
        assert require_role("viewer", "generate_code") is False
        assert require_role("viewer", "merge") is False

    def test_developer_can_develop_not_merge(self) -> None:
        assert require_role("developer", "task.execute") is True
        assert require_role("developer", "refactor") is True
        assert require_role("developer", "merge") is False
        assert require_role("developer", "main_branch_write") is False

    def test_admin_everything(self) -> None:
        assert require_role("admin", "merge") is True
        assert require_role("admin", "manage_users") is True
        assert require_role("admin", "task.read") is True

    def test_unknown_role_denied(self) -> None:
        assert require_role("hacker", "task.read") is False

    def test_unknown_operation_requires_admin(self) -> None:
        assert require_role("developer", "warp_drive") is False
        assert require_role("admin", "warp_drive") is True

    def test_allowed_operations_ordering(self) -> None:
        ops = allowed_operations("viewer")
        assert "task.read" in ops
        assert "merge" not in ops
        assert len(allowed_operations("developer")) > len(ops)

    def test_check_permission_structure(self) -> None:
        result = check_permission("developer", "merge")
        assert result["allowed"] is False
        assert result["required_role"] == "admin"
        result2 = check_permission(None, "task.read")
        assert result2["allowed"] is True
        assert result2["role"] == "viewer"
