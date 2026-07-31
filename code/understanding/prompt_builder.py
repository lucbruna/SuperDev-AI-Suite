from __future__ import annotations

import logging
from typing import Any

from .context_builder import estimate_tokens

#: Marker inserted where a file's middle was truncated.
_TRUNCATION_MARKER = "# ... [{removed} lines / ~{tokens} tokens truncated] ..."

#: Token cost reserved for the marker line inside the line-based head/tail
#: split of :meth:`_truncate_to_budget`. The exact removed-line count is
#: unknown until the split is computed, so a conservative fixed reserve keeps
#: the assembled slice within its budget (the post-assembly verify + the
#: char-slice fallback cover any residual overshoot).
_MARKER_RESERVE = 12

#: Safety margin applied by the line-based verify of :meth:`_truncate_to_budget`.
#: ``estimate_tokens`` floors each part, so a slice that fits *budget* by its
#: own estimate can still overshoot by 1-2 tokens once the ``### FILE``
#: header/footer are joined in (e.g. parts sum to 29 tokens while the joined
#: block is 120 chars -> 30). Reserving a small margin routes those
#: boundary slices to :meth:`_char_slice` (which has its own 4-token margin),
#: so the global re-check ``tokens(block) <= remaining`` truncates instead of
#: dropping the file.
_SLICE_VERIFY_MARGIN = 2

#: Short marker used by the guaranteed-fit char-slice fallback.
_CHAR_MARKER = "# ... [truncated] ..."


def _block_overhead(path: str) -> int:
    """Fixed token cost of a ``### FILE`` block around the content (header
    fence + closing fence). Used to reserve room for it when a file is
    truncated to a global budget."""
    header = f"### FILE: {path}\n```\n"
    footer = "\n```"
    return estimate_tokens(header) + estimate_tokens(footer)


class PromptBuilder:
    """Builds an LLM prompt by injecting the context selected by
    :class:`ContextBuilder` (or any ``path``/``content`` list) under the
    instruction.

    Two budgets are respected:

    - ``max_file_tokens`` caps each injected file individually: files that
      exceed it are truncated **in the middle** (keeping the head and the
      tail — where imports and trailing definitions usually live).
    - ``max_tokens`` caps the **whole prompt**: if the assembled prompt still
      exceeds it, trailing files (the least relevant, since selections are
      ranked) are truncated further — and, when even a minimal slice cannot
      fit, dropped entirely.

    Truncated paths are tracked in :attr:`last_truncated` and dropped paths
    in :attr:`last_dropped`.
    """

    def __init__(self, max_tokens: int = 16000,
                 max_file_tokens: int | None = None) -> None:
        self.max_tokens = max(1, max_tokens)
        # None disables per-file truncation (backward-compatible).
        self.max_file_tokens = (max(1, max_file_tokens)
                                if max_file_tokens else None)
        self.last_truncated: list[str] = []
        self.last_dropped: list[str] = []
        self._log = logging.getLogger("superdev.code.understanding.prompt")

    def build(self, instruction: str,
              context_files: list[dict[str, Any]] | None = None) -> str:
        """Compose *instruction* + file blocks into a single prompt string.

        First, files whose estimated tokens exceed ``max_file_tokens`` are
        truncated in the middle (see :meth:`_truncate_content`). Then the
        **global budget** is enforced: while the assembled prompt exceeds
        ``max_tokens``, the trailing file (least relevant) is truncated in
        the middle down to the remaining budget; if even its minimal slice
        cannot fit, the file is dropped. Truncated paths are recorded in
        :attr:`last_truncated` and dropped paths in :attr:`last_dropped`.
        """
        context_files = list(context_files or [])
        self.last_truncated = []
        self.last_dropped = []

        # Per-file pass: apply max_file_tokens middle-truncation.
        files: list[tuple[str, str]] = []
        for file in context_files:
            path = file.get("path", "<unknown>")
            content = file.get("content", "")
            files.append((path, self._truncate_content(path, content)))

        def assemble(remaining_files: list[tuple[str, str]]) -> str:
            parts = [instruction.strip()]
            for path, content in remaining_files:
                parts.append(self._make_block(path, content))
            return "\n\n".join(parts)

        # Global pass: tighten from the tail until the prompt fits.
        while files and self.tokens(assemble(files)) > self.max_tokens:
            path, content = files[-1]
            remaining = self.max_tokens - self.tokens(assemble(files[:-1]))
            if remaining > _block_overhead(path):
                target = max(1, remaining - _block_overhead(path))
                shrunk = self._truncate_to_budget(content, target)
                # ``shrunk != content`` guarantees progress: when the slice
                # already fits *target* the content comes back unchanged and
                # a ``continue`` would spin forever (the joined ``assemble``
                # estimate can exceed ``max_tokens`` by 1-2 floor remainders
                # even when the block fits *remaining*). In that case the
                # file is dropped instead — termination is guaranteed.
                if (shrunk != content
                        and self.tokens(self._make_block(path, shrunk))
                        <= remaining):
                    files[-1] = (path, shrunk)
                    if path not in self.last_truncated:
                        self.last_truncated.append(path)
                    continue
            # Even the minimal slice does not fit the remaining budget.
            files.pop()
            self.last_dropped.append(path)

        return assemble(files)

    def _make_block(self, path: str, content: str) -> str:
        """Render one ``### FILE`` fenced block."""
        return f"### FILE: {path}\n```\n{content}\n```"

    def _truncate_content(self, path: str, content: str) -> str:
        """Truncate *content* in the middle when it exceeds the per-file
        budget (``max_file_tokens``), keeping the head and the tail with a
        marker line.

        Returns *content* unchanged when truncation is disabled or the
        content fits. Records *path* in :attr:`last_truncated` when a
        truncation actually happened.
        """
        if self.max_file_tokens is None:
            return content
        if estimate_tokens(content) <= self.max_file_tokens:
            return content
        self.last_truncated.append(path)
        return self._truncate_to_budget(content, self.max_file_tokens)

    def _truncate_to_budget(self, content: str, budget: int) -> str:
        """Truncate *content* in the middle to fit *budget* tokens.

        Keeps the head lines that fit the first half of the budget and the
        tail lines that fit the rest, with a marker line in between. When a
        single line already exceeds the budget — or the assembled slice
        still overshoots (per-line estimates miss the joined newlines and
        the marker digits) — falls back to :meth:`_char_slice`, which is
        guaranteed to fit. Returns *content* unchanged when it already fits.
        """
        budget = max(1, budget)
        if estimate_tokens(content) <= budget:
            return content

        lines = content.splitlines()
        if not lines:
            return content

        # Reserve room for the marker line inside the split budget: without
        # it the line-based slice would overshoot once the marker's ~12
        # tokens are joined in (see the verify below).
        usable = max(1, budget - _MARKER_RESERVE)
        head_budget = usable // 2
        tail_budget = usable - head_budget

        # Head: keep the first lines while they fit in half the budget.
        head_end = 0
        head_tokens = 0
        while head_end < len(lines):
            line_tokens = estimate_tokens(lines[head_end])
            if head_tokens + line_tokens > head_budget:
                break
            head_tokens += line_tokens
            head_end += 1

        # Tail: keep the last lines while they fit in the remaining budget.
        tail_start = len(lines)
        tail_tokens = 0
        while tail_start > head_end:
            line_tokens = estimate_tokens(lines[tail_start - 1])
            if tail_tokens + line_tokens > tail_budget:
                break
            tail_tokens += line_tokens
            tail_start -= 1

        if head_end == 0 or tail_start == len(lines):
            # A single line already exceeds the budget — char-slice it.
            return self._char_slice(content, budget)

        removed = tail_start - head_end
        removed_tokens = sum(estimate_tokens(line)
                             for line in lines[head_end:tail_start])
        marker = _TRUNCATION_MARKER.format(removed=removed,
                                           tokens=removed_tokens)
        result = "\n".join(lines[:head_end] + [marker] + lines[tail_start:])
        # Verify with a margin: the slice's own estimate can pass while the
        # enclosing ``### FILE`` block still overshoots the *remaining*
        # budget in the global pass (see ``_SLICE_VERIFY_MARGIN``).
        if estimate_tokens(result) > budget - _SLICE_VERIFY_MARGIN:
            # The joined slice overshot the estimate (newlines + marker
            # digits) — fall back to the guaranteed-fit char slice.
            return self._char_slice(content, budget)
        return result

    @staticmethod
    def _char_slice(content: str, budget: int) -> str:
        """Middle-truncate *content* by characters to fit *budget* tokens.

        Keeps the head and the tail (``~4 chars/token``) with a short fixed
        marker in between. The marker's cost is reserved up-front, so the
        returned string is **guaranteed** to fit *budget* — unlike the
        line-based split, whose joined estimate can overshoot.
        """
        marker_tokens = estimate_tokens(_CHAR_MARKER)
        # Reserve the marker plus a safety margin for the two newlines and
        # floor-division remainders. The extra 4 tokens give headroom so the
        # enclosing ``### FILE`` block still fits the *remaining* budget in
        # the global pass (whose re-check decides truncate vs drop).
        usable = max(1, budget - marker_tokens - 4)
        chars = usable * 4
        head_chars = chars // 2
        tail_chars = chars - head_chars
        head = content[:head_chars].rstrip()
        if not head:
            # Leading blank lines consumed the whole head — give its chars
            # to the tail so the slice keeps meaningful content (e.g. the
            # ``"zzzz"`` of a ``"\n\n" + "z" * 2000`` single-line file).
            head_chars = 0
            tail_chars = min(len(content), chars)
        tail = content[-tail_chars:].lstrip() if tail_chars else ""
        return f"{head}\n{_CHAR_MARKER}\n{tail}"

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
