"""Progress bar formatter for CLI."""

import sys


def progress_bar(current: int, total: int, width: int = 40, prefix: str = "") -> str:
    pct = current / total if total > 0 else 0
    filled = int(width * pct)
    bar = "=" * filled + "-" * (width - filled)
    return f"\r{prefix} [{bar}] {pct:.0%} ({current}/{total})"


def show_progress(current: int, total: int, prefix: str = "") -> None:
    sys.stdout.write(progress_bar(current, total, prefix=prefix))
    sys.stdout.flush()
    if current == total:
        print()
