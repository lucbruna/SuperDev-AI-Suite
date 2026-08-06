"""Unit tests for the AI Code Knowledge Graph scanner package (phase 1).

Covers the filesystem walk (category assignment, ignore rules, safety caps),
the end-to-end project scan (per-language dispatch, parsed payloads, error
records) and the knowledge pipeline scan stage. Tests use a small temp
fixture project so nothing scans the real repository.
"""
from __future__ import annotations

import pytest

from modules.ai_code_knowledge_graph.config.knowledge_config import KnowledgeConfig
from modules.ai_code_knowledge_graph.core.knowledge_context import KnowledgeContext
from modules.ai_code_knowledge_graph.core.knowledge_pipeline import KnowledgePipeline
from modules.ai_code_knowledge_graph.scanner import ProjectScanner, language_for_file, scan_files
from modules.ai_code_knowledge_graph.scanner.filesystem_scanner import FileInfo


# ------------------------------------------------------------------ fixtures
def _write(root, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture()
def fixture_root(tmp_path) -> object:
    root = tmp_path / "fixture"
    _write(root, "src/app.py", "from lib import helper\n\ndef main():\n    return helper()\n")
    _write(root, "src/lib.js", "export const answer = 42;\n")
    _write(root, "src/ui.tsx", "export function Button() { return null; }\n")
    _write(root, "src/data.json", '{"name": "superdev"}\n')
    _write(root, "config/settings.yaml", "name: settings\nenabled: true\n")
    _write(root, "docs/guide.md", "# Guide\n\nSome docs.\n")
    _write(root, "Dockerfile", "FROM python:3.12\nWORKDIR /app\n")
    _write(root, ".gitignore", "*.pyc\n.superdev/\n")
    _write(root, "workflows/release.yml", "name: release\non: push\n")
    _write(root, "plugins/plugin.json", '{"name": "demo", "version": "1.0.0"}\n')
    _write(root, "db/schema.sql", "CREATE TABLE users (id INTEGER PRIMARY KEY);\n")
    # Files that must be skipped.
    _write(root, "src/binary.py", b"\x00\x01\x02binary".decode("latin-1"))
    _write(root, "src/node_modules/pkg/index.js", "module.exports = 1;\n")
    _write(root, "src/bundle.min.js", "var a=1;\n")
    _write(root, "src/.hidden.py", "x = 1\n")
    return root


def _scanner_config(root, **overrides):
    from modules.ai_code_knowledge_graph.config.scanner_config import ScannerConfig

    cfg = ScannerConfig()
    cfg.project_root = str(root)
    cfg.project_dirs = ("src", "config", "docs", "workflows", "plugins", "db")
    cfg.scan_frontend = False
    for key, value in overrides.items():
        setattr(cfg, key, value)
    return cfg


# ------------------------------------------------------- filesystem scanning
class TestFilesystemScanner:
    def test_language_for_file_categories(self) -> None:
        assert language_for_file("src/app.py") == "python"
        assert language_for_file("src/lib.js") == "javascript"
        assert language_for_file("src/ui.tsx") == "typescript"
        assert language_for_file("src/data.json") == "json"
        assert language_for_file("config/settings.yaml") == "yaml"
        assert language_for_file("docs/guide.md") == "markdown"
        assert language_for_file("db/schema.sql") == "database"
        assert language_for_file("Dockerfile") == "docker"
        assert language_for_file(".gitignore") == "git"
        assert language_for_file("plugins/plugin.json") == "plugin"
        assert language_for_file("workflows/release.yml") == "workflow"
        assert language_for_file("unknown.xyz") == ""

    def test_scan_files_honors_ignores_and_caps(self, fixture_root) -> None:
        config = _scanner_config(fixture_root)
        files = scan_files(config)
        rels = {info.rel_path for info in files}
        assert "src/app.py" in rels
        assert "Dockerfile" in rels
        assert ".gitignore" in rels  # hidden but allowlisted as git metadata
        assert "workflows/release.yml" in rels
        assert "plugins/plugin.json" in rels
        assert "db/schema.sql" in rels
        # Ignored: nested node_modules, minified bundles, hidden files.
        assert not any("node_modules" in rel for rel in rels)
        assert not any(rel.endswith(".min.js") for rel in rels)
        assert "src/.hidden.py" not in rels
        assert "src/binary.py" in rels  # walked by extension, fails at content read

    def test_scan_files_max_cap(self, fixture_root) -> None:
        config = _scanner_config(fixture_root, max_files=2)
        files = scan_files(config)
        assert len(files) <= 2

    def test_file_info_shape(self, fixture_root) -> None:
        config = _scanner_config(fixture_root)
        info = next(i for i in scan_files(config) if i.rel_path == "src/app.py")
        assert isinstance(info, FileInfo)
        assert info.language == "python"
        assert info.size > 0
        assert info.mtime > 0


# ------------------------------------------------------------ project scanner
class TestProjectScanner:
    def test_scan_returns_expected_shape(self, fixture_root) -> None:
        result = ProjectScanner(_scanner_config(fixture_root)).scan()
        assert result["project_root"] == str(fixture_root)
        assert isinstance(result["files"], list)
        assert isinstance(result["errors"], list)
        assert "by_language" in result["stats"]
        assert result["stats"]["files"] == len(result["files"])
        assert result["stats"]["errors"] == len(result["errors"])

    def test_scan_dispatches_parsed_payloads(self, fixture_root) -> None:
        result = ProjectScanner(_scanner_config(fixture_root)).scan()
        by_path = {entry["rel_path"]: entry for entry in result["files"]}

        app = by_path["src/app.py"]
        assert app["language"] == "python"
        assert app["parsed"]["language"] == "python"
        assert app["parsed"]["rel_path"] == "src/app.py"
        assert app["parsed"]["entities"][0]["kind"] == "file"  # stub until parsers ship
        assert app["parsed"]["error"] is None

        assert by_path["Dockerfile"]["language"] == "docker"
        assert by_path[".gitignore"]["language"] == "git"
        assert by_path["workflows/release.yml"]["language"] == "workflow"
        assert by_path["plugins/plugin.json"]["language"] == "plugin"
        assert by_path["db/schema.sql"]["language"] == "database"

        languages = {entry["language"] for entry in result["files"]}
        assert {
            "python",
            "javascript",
            "typescript",
            "json",
            "yaml",
            "markdown",
            "docker",
            "git",
            "workflow",
            "plugin",
            "database",
        } <= languages

    def test_scan_records_binary_error(self, fixture_root) -> None:
        result = ProjectScanner(_scanner_config(fixture_root)).scan()
        binary_errors = [e for e in result["errors"] if "binary" in e["error"]]
        assert binary_errors, "binary fixture should surface as a scan error"
        assert binary_errors[0]["rel_path"] == "src/binary.py"

    def test_scan_raises_for_missing_root(self, tmp_path) -> None:
        scanner = ProjectScanner(_scanner_config(tmp_path / "nope"))
        with pytest.raises(Exception):
            scanner.scan()


# ---------------------------------------------------------- pipeline scan stage
class TestPipelineScanStage:
    def test_scan_stage_via_pipeline(self, fixture_root) -> None:
        config = KnowledgeConfig()
        config.scanner.project_root = str(fixture_root)
        config.scanner.project_dirs = ("src", "config", "docs", "workflows", "plugins", "db")
        config.scanner.scan_frontend = False

        ctx = KnowledgeContext(config=config)
        pipeline = KnowledgePipeline()
        summary = pipeline.run(ctx)

        assert summary["stages"][0]["name"] == "scan"
        assert summary["stages"][0]["files"] >= 10
        assert ctx.stats["files_scanned"] >= 10
        assert ctx.memory.get("scan_result") is not None
        assert ctx.state.to_dict()["state"] == "ready"
