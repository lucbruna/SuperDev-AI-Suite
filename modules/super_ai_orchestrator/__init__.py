"""Super AI Orchestrator Core — the central coordinator of the SuperDev suite.

Volume 6 of the SuperDev AI Suite advanced modules. This module connects
absolutely everything: it decides who executes each task, which LLM serves
it and what tools it needs, then orchestrates the sibling modules through
graceful, non-invasive connectors.

Pipeline::

    task ─▶ decision (owner, llm, tools) ─▶ governance gate
        ─▶ planning ─▶ execution (kernel) ─▶ audit ─▶ reports

Everything in the core is deterministic: the same task state always produces
the same decision and the same execution order. No clock, network or LLM
calls happen inside the core.
"""
from __future__ import annotations

from modules.super_ai_orchestrator.version import VERSION, __version__

__all__ = ["VERSION", "__version__"]
