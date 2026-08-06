"""Autonomous Developer — self-directed coding agent for the SuperDev AI Suite.

The Autonomous Developer consumes the Architecture Intelligence graph and the
AI Code Knowledge Graph to plan, generate, modify, test, document and improve
code with minimal supervision. Every change runs on a dedicated work branch,
is validated and tested, and is submitted for review before anything touches a
main branch.

Operation flow::

    user request ─▶ Architecture Intelligence ─▶ AI Code Knowledge Graph
        ─▶ Project Planner ─▶ Task Planner ─▶ Code Generator
        ─▶ Refactoring Engine ─▶ Validation Engine ─▶ Test Generator
        ─▶ Code Reviewer ─▶ Documentation Writer ─▶ Git/GitHub ─▶ Deployment
"""
from __future__ import annotations

from modules.autonomous_developer.version import __version__

__all__ = ["__version__"]
