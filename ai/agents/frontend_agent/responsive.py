from __future__ import annotations

from typing import Any

DEFAULT_BREAKPOINTS: dict[str, int] = {
    "mobile": 0,
    "tablet": 768,
    "desktop": 1024,
    "wide": 1440,
}


class Responsive:
    """Manages responsive breakpoints and generates media queries."""

    def __init__(self) -> None:
        self._breakpoints: dict[str, dict[str, Any]] = {}
        for name, width in DEFAULT_BREAKPOINTS.items():
            self._breakpoints[name] = {"name": name, "min_width": width}

    def add_breakpoint(self, name: str, min_width: int) -> str:
        self._breakpoints[name] = {"name": name, "min_width": min_width}
        return name

    def get_breakpoint(self, name: str) -> dict[str, Any] | None:
        return self._breakpoints.get(name)

    def remove_breakpoint(self, name: str) -> bool:
        if name in self._breakpoints:
            del self._breakpoints[name]
            return True
        return False

    def list_breakpoints(self) -> list[dict[str, Any]]:
        return sorted(self._breakpoints.values(), key=lambda b: b["min_width"])

    @property
    def breakpoint_count(self) -> int:
        return len(self._breakpoints)

    def generate_media_queries(self) -> str:
        bps = self.list_breakpoints()
        lines = ["/* Responsive Breakpoints */"]
        for bp in bps:
            lines.append(f"\n/* {bp['name']} */")
            lines.append(f"@media (min-width: {bp['min_width']}px) {{")
            lines.append(f"  /* {bp['name']} styles */")
            lines.append("}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "breakpoints": self.list_breakpoints(),
            "breakpoint_count": self.breakpoint_count,
        }
