"""AST layer — normalized entity extraction from source code.

Defines the canonical entity schema (:mod:`.entities`) and the language AST
extractors (:mod:`.python_ast`) that the parser package builds on.
"""
from __future__ import annotations

from modules.ai_code_knowledge_graph.ast import entities, python_ast
from modules.ai_code_knowledge_graph.ast.entities import make_entity

__all__ = ["entities", "make_entity", "python_ast"]
