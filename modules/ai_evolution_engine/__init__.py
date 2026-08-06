"""AI Evolution Engine — continuous platform evolution analysis for SuperDev.

The AI Evolution Engine observes the platform as a whole and answers
questions like::

    * Where is there excessive coupling?
    * Which modules grew too large and should be split?
    * Which components carry the most technical debt?
    * Which architectural improvements yield the most benefit?
    * How should evolutions be prioritised for the next releases?

Unlike the Self-Healing Engine (which *fixes*), this module *proposes*: it
produces analyses, recommendations and evolution plans that other modules
(Autonomous Developer, Self-Healing Engine) may consume, always respecting
the project's approval flow. Nothing is modified automatically.

Pipeline::

    platform state ─▶ analytics ─▶ evolution analysis ─▶ learning
        ─▶ recommendations ─▶ forecasting ─▶ governance approval
        ─▶ roadmap ─▶ reports
"""
from __future__ import annotations

from modules.ai_evolution_engine.version import VERSION, __version__

__all__ = ["VERSION", "__version__"]
