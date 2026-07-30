from __future__ import annotations

from typing import Any


class Flamegraph:
    """Generates flamegraph-compatible output from profiling samples."""

    def __init__(self) -> None:
        self._stacks: dict[str, int] = {}

    def add_sample(self, stack: list[str], count: int = 1) -> None:
        key = ";".join(stack)
        self._stacks[key] = self._stacks.get(key, 0) + count

    def to_folded(self) -> str:
        lines: list[str] = []
        for stack, count in sorted(self._stacks.items()):
            lines.append(f"{stack} {count}")
        return "\n".join(lines)

    def to_svg_data(self, title: str = "Flamegraph") -> dict[str, Any]:
        total = sum(self._stacks.values())
        frames: list[dict[str, Any]] = []

        for stack, count in sorted(self._stacks.items(), key=lambda x: -x[1]):
            frames.append({
                "name": stack.split(";")[-1] if ";" in stack else stack,
                "stack": stack,
                "value": count,
                "percentage": round(count / total * 100, 2) if total else 0,
            })

        return {
            "title": title,
            "total_samples": total,
            "unique_stacks": len(self._stacks),
            "frames": frames,
        }

    def reset(self) -> None:
        self._stacks.clear()
