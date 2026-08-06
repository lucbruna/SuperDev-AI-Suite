"""Shared constants for the AI Code Knowledge Graph module.

Values follow the same conventions as the Architecture Graph module:
defaults live here, overridable through ``SUPERDEV_KG_*`` environment
variables in the per-area configs.
"""
from __future__ import annotations

# Runtime data lives under <project>/.superdev/ai_code_knowledge_graph/
DATA_DIR_NAME = ".superdev"
MODULE_DATA_DIR = "ai_code_knowledge_graph"
DEFAULT_DB_FILE = "knowledge_graph.db"
DEFAULT_SNAPSHOT_FILE = "knowledge_snapshot.json"
DEFAULT_EXPORT_DIR = "exports"
DEFAULT_VECTOR_DIR = "vectors"
DEFAULT_REPORT_DIR = "reports"

# Directories scanned by default when scanning the whole repository.
PROJECT_DIRS: tuple[str, ...] = ("modules", "backend", "frontend", "tests", "docs", "scripts")
FRONTEND_DIRS: tuple[str, ...] = ("frontend/src", "frontend/app", "frontend/components", "frontend/pages")

# Directories never scanned (matches any depth).
IGNORE_DIRS: frozenset[str] = frozenset({
    ".git", ".hg", ".svn", ".next", ".nuxt", "node_modules", "bower_components",
    "__pycache__", ".venv", "venv", "env", "dist", "build", "out", ".cache",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", ".coverage", "coverage", "htmlcov",
    ".superdev", "downloads", ".terraform", "workspace", ".mantis_snapshots",
    ".idea", ".vscode", ".slim", ".next", "staticfiles", ".turbo",
})

# File name patterns never scanned (glob-style).
IGNORE_FILES: frozenset[str] = frozenset({
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "npm-shrinkwrap.json",
    "*.min.js", "*.min.css", "*.map", "*.pyc", "*.pyo", "*.so", "*.dll", "*.dylib",
    "*.exe", "*.db", "*.sqlite", "*.sqlite3", "*.log", "*.lock",
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp", "*.ico", "*.bmp",
    "*.woff", "*.woff2", "*.ttf", "*.eot", "*.otf", "*.pdf", "*.zip", "*.gz", "*.tar",
    ".DS_Store", "Thumbs.db", "*.bak", "*.tmp",
})

# Extension → language mapping used by the scanners.
LANGUAGE_EXTENSIONS: dict[str, str] = {
    ".py": "python",
    ".pyi": "python",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".mts": "typescript",
    ".cts": "typescript",
    ".tsx": "typescript",
    ".json": "json",
    ".jsonc": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".xml": "xml",
    ".md": "markdown",
    ".markdown": "markdown",
    ".mdx": "markdown",
    ".rst": "markdown",
    ".toml": "yaml",
    ".ini": "yaml",
    ".cfg": "yaml",
    ".conf": "yaml",
    ".sql": "sql",
}

# Kind names for graph nodes.
NODE_KIND_MODULE = "module"
NODE_KIND_FILE = "file"
NODE_KIND_CLASS = "class"
NODE_KIND_FUNCTION = "function"
NODE_KIND_API = "api"
NODE_KIND_DATABASE = "database"
NODE_KIND_TABLE = "table"
NODE_KIND_AGENT = "agent"
NODE_KIND_PLUGIN = "plugin"
NODE_KIND_WORKFLOW = "workflow"
NODE_KIND_PROMPT = "prompt"
NODE_KIND_MCP_TOOL = "mcp_tool"
NODE_KIND_EVENT = "event"
NODE_KIND_CONFIG = "config"

# Edge kind names for graph relations.
EDGE_KIND_IMPORTS = "imports"
EDGE_KIND_CALLS = "calls"
EDGE_KIND_INHERITS = "inherits"
EDGE_KIND_CONTAINS = "contains"
EDGE_KIND_DEPENDS = "depends_on"
EDGE_KIND_IMPLEMENTS = "implements"
EDGE_KIND_TRIGGERS = "triggers"
EDGE_KIND_LISTENS = "listens"
EDGE_KIND_SEMANTIC = "semantically_related"
