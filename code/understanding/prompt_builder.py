from __future__ import annotations

import logging
from typing import Any

from .context_builder import estimate_tokens


class PromptBuilder:
    """Builds an LLM prompt by injecting the context selected by
    :class:`ContextBuilder` (or any ``path``/``content`` list) under the
    instruction."""

    def __init__(self, max_tokens: int = 16000) -> None:
        self.max_tokens = max(1, max_tokens)
        self._log = logging.getLogger("superdev.code.understanding.prompt")

    def build(self, instruction: str,
              context_files: list[dict[str, Any]] | None = None) -> str:
        """Compose *instruction* + file blocks into a single prompt string."""
        context_files = list(context_files or [])
        parts = [instruction.strip()]
        for file in context_files:
            path = file.get("path", "<unknown>")
            content = file.get("content", "")
            parts.append(f"### FILE: {path}\n```\n{content}\n```")
        return "\n\n".join(parts)

    def build_from_selection(
        self,
        instruction: str,
        selection: list[dict[str, Any]],
        files_by_path: dict[str, str],
    ) -> str:
        """Build a prompt from a ContextBuilder selection + content map."""
        context_files = [{"path": entry["path"],
                          "content": files_by_path.get(entry["path"], "")}
                         for entry in selection]
        return self.build(instruction, context_files)

    def tokens(self, prompt: str) -> int:
        """Estimated token count of a composed prompt."""
        return estimate_tokens(prompt)

    def fits_budget(self, prompt: str) -> bool:
        """True when *prompt* fits the configured token budget."""
        return self.tokens(prompt) <= self.max_tokens
