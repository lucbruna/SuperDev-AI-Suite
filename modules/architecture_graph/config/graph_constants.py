"""Constants shared across the Architecture Graph module."""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Filesystem / discovery
# ---------------------------------------------------------------------------

# Top-level project directories that participate in the graph. Relative to the
# repository root. Frontend-only dirs are listed separately because they are
# mapped into a lighter subgraph unless full scanning is enabled.
PROJECT_DIRS: tuple[str, ...] = (
    "modules",
    "backend",
    "core",
    "ai",
    "cli",
    "scanners",
    "security",
    "builders",
    "runtime_engine",
    "workflow_engine",
    "automation",
    "integration",
    "infrastructure",
    "docs",
)

FRONTEND_DIRS: tuple[str, ...] = ("frontend",)

# Directories/files that are never indexed (build artifacts, caches, vendors).
IGNORE_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".agents",
        ".claude",
        ".cursor",
        ".windsurf",
        ".mimocode",
        ".github",
        ".slim",
        ".knowledge",
        "dist",
        "build",
        "exports",
        "backups",
        "data",
        "downloads",
        "coverage",
        "htmlcov",
        ".next",
        "out",
        "assets",
        "static",
        "public",
    }
)

IGNORE_FILES: frozenset[str] = frozenset(
    {
        ".env",
        ".env.local",
        "*.pyc",
        "*.pyo",
        "*.so",
        "*.dll",
        "*.exe",
        "*.png",
        "*.jpg",
        "*.jpeg",
        "*.gif",
        "*.webp",
        "*.ico",
        "*.svg",
        "*.woff",
        "*.woff2",
        "*.ttf",
        "*.eot",
        "*.pdf",
        "*.lock",
        "package-lock.json",
        "pnpm-lock.yaml",
        "yarn.lock",
        "coverage.json",
    }
)

# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

EXTENSION_LANG: dict[str, str] = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".md": "markdown",
    ".rst": "markdown",
    ".sql": "sql",
    ".html": "html",
    ".css": "css",
    ".dockerfile": "docker",
    ".sh": "shell",
    ".ps1": "shell",
    ".proto": "proto",
}

SCANNABLE_EXTENSIONS: frozenset[str] = frozenset(EXTENSION_LANG)

# ---------------------------------------------------------------------------
# Graph semantics
# ---------------------------------------------------------------------------

NODE_KINDS: tuple[str, ...] = (
    "module",      # native platform module (modules/<name>)
    "package",     # top-level package (backend, core, ai, ...)
    "file",
    "class",
    "function",
    "api",         # REST endpoint / API route
    "plugin",
    "agent",
    "workflow",
    "database",
    "table",
    "service",     # external service (redis, postgres, neo4j, ...)
    "config",
    "document",
    "external",    # third-party dependency
)

EDGE_KINDS: tuple[str, ...] = (
    "contains",
    "imports",
    "calls",
    "uses",
    "depends_on",
    "implements",
    "deploys",
    "executes",
    "reads",
    "writes",
    "configured_by",
    "exposes",       # backend router → api endpoint
    "consumes",      # frontend / agent → api endpoint
    "orchestrates",
)

# ---------------------------------------------------------------------------
# Layering (topology engine)
# ---------------------------------------------------------------------------

LAYERS: dict[str, str] = {
    "frontend": "frontend",
    "backend": "backend",
    "modules": "modules",
    "core": "core",
    "ai": "ai",
    "workflow_engine": "workflow_engine",
    "runtime_engine": "runtime_engine",
    "cli": "cli",
    "infrastructure": "infrastructure",
    "docs": "docs",
    "external": "external",
}

# Layer order (index 0 = lowest level, must not import higher layers).
LAYER_ORDER: tuple[str, ...] = (
    "infrastructure",
    "core",
    "ai",
    "workflow_engine",
    "runtime_engine",
    "modules",
    "backend",
    "cli",
    "frontend",
    "external",
    "docs",
)

# Entry points used by the orphan detector: files that may legally have no
# dependents because they are bootstrap/CLI/entry files.
ENTRYPOINTS: tuple[str, ...] = (
    "main.py",
    "app.py",
    "manage.py",
    "cli.py",
    "run.py",
    "wsgi.py",
    "asgi.py",
    "setup.py",
    "setup.ps1",
    "run_mantis.py",
    "test_sbom.py",
)

# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

DEFAULT_DATA_DIR_NAME = "data"
DEFAULT_DB_FILE = "architecture_graph.db"
DEFAULT_SNAPSHOT_FILE = "file_snapshot.json"
DEFAULT_EXPORT_DIR = "exports"
