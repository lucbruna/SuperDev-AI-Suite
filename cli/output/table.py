"""Table output formatter for CLI."""


def format_table(headers: list[str], rows: list[list[str]], compact: bool = False) -> str:
    if not rows:
        return "(no data)"

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    sep = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    header_row = "|" + "|".join(f" {h:<{col_widths[i]}}" for i, h in enumerate(headers)) + "|"

    lines = [sep, header_row, sep]
    for row in rows:
        line = "|" + "|".join(f" {str(row[i]):<{col_widths[i]}}" for i in range(len(headers))) + "|"
        lines.append(line)
    lines.append(sep)

    return "\n".join(lines)
