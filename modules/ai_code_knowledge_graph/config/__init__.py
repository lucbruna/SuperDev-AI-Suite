"""Configuration models for the AI Code Knowledge Graph.

Plain dataclasses with ``SUPERDEV_KG_*`` environment overrides so the module
works with zero hard dependencies. Use :func:`get_default_config` to obtain
a fully resolved configuration rooted at the repository.
"""
from __future__ import annotations

from modules.ai_code_knowledge_graph.config.constants import (
    DATA_DIR_NAME,
    DEFAULT_DB_FILE,
    DEFAULT_EXPORT_DIR,
    DEFAULT_SNAPSHOT_FILE,
    DEFAULT_VECTOR_DIR,
    EDGE_KIND_CALLS,
    EDGE_KIND_CONTAINS,
    EDGE_KIND_DEPENDS,
    EDGE_KIND_IMPLEMENTS,
    EDGE_KIND_IMPORTS,
    EDGE_KIND_INHERITS,
    EDGE_KIND_LISTENS,
    EDGE_KIND_SEMANTIC,
    EDGE_KIND_TRIGGERS,
    FRONTEND_DIRS,
    IGNORE_DIRS,
    IGNORE_FILES,
    LANGUAGE_EXTENSIONS,
    MODULE_DATA_DIR,
    NODE_KIND_AGENT,
    NODE_KIND_API,
    NODE_KIND_CLASS,
    NODE_KIND_CONFIG,
    NODE_KIND_DATABASE,
    NODE_KIND_EVENT,
    NODE_KIND_FILE,
    NODE_KIND_FUNCTION,
    NODE_KIND_MCP_TOOL,
    NODE_KIND_MODULE,
    NODE_KIND_PLUGIN,
    NODE_KIND_PROMPT,
    NODE_KIND_TABLE,
    NODE_KIND_WORKFLOW,
    PROJECT_DIRS,
)
from modules.ai_code_knowledge_graph.config.cache_config import CacheConfig
from modules.ai_code_knowledge_graph.config.database_config import DatabaseConfig
from modules.ai_code_knowledge_graph.config.embedding_config import EmbeddingConfig
from modules.ai_code_knowledge_graph.config.graph_config import GraphConfig
from modules.ai_code_knowledge_graph.config.knowledge_config import KnowledgeConfig
from modules.ai_code_knowledge_graph.config.llm_config import LLMConfig
from modules.ai_code_knowledge_graph.config.permissions import (
    allowed_operations,
    check_permission,
    require_role,
)
from modules.ai_code_knowledge_graph.config.scanner_config import ScannerConfig
from modules.ai_code_knowledge_graph.config.semantic_config import SemanticConfig


def get_default_config() -> KnowledgeConfig:
    """Build a resolved default knowledge configuration for the repository."""
    config = KnowledgeConfig.from_env()
    config.resolve()
    return config


__all__ = [
    "DATA_DIR_NAME",
    "DEFAULT_DB_FILE",
    "DEFAULT_EXPORT_DIR",
    "DEFAULT_SNAPSHOT_FILE",
    "DEFAULT_VECTOR_DIR",
    "EDGE_KIND_CALLS",
    "EDGE_KIND_CONTAINS",
    "EDGE_KIND_DEPENDS",
    "EDGE_KIND_IMPLEMENTS",
    "EDGE_KIND_IMPORTS",
    "EDGE_KIND_INHERITS",
    "EDGE_KIND_LISTENS",
    "EDGE_KIND_SEMANTIC",
    "EDGE_KIND_TRIGGERS",
    "FRONTEND_DIRS",
    "IGNORE_DIRS",
    "IGNORE_FILES",
    "LANGUAGE_EXTENSIONS",
    "MODULE_DATA_DIR",
    "NODE_KIND_AGENT",
    "NODE_KIND_API",
    "NODE_KIND_CLASS",
    "NODE_KIND_CONFIG",
    "NODE_KIND_DATABASE",
    "NODE_KIND_EVENT",
    "NODE_KIND_FILE",
    "NODE_KIND_FUNCTION",
    "NODE_KIND_MCP_TOOL",
    "NODE_KIND_MODULE",
    "NODE_KIND_PLUGIN",
    "NODE_KIND_PROMPT",
    "NODE_KIND_TABLE",
    "NODE_KIND_WORKFLOW",
    "PROJECT_DIRS",
    "CacheConfig",
    "DatabaseConfig",
    "EmbeddingConfig",
    "GraphConfig",
    "KnowledgeConfig",
    "LLMConfig",
    "ScannerConfig",
    "SemanticConfig",
    "allowed_operations",
    "check_permission",
    "get_default_config",
    "require_role",
]
