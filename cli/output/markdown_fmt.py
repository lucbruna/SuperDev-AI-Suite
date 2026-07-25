"""Markdown output formatter for CLI."""


def format_markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "(no data)"

    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")

    return "\n".join(lines)
