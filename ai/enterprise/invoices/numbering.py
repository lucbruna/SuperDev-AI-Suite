"""Invoice numbering."""

from __future__ import annotations


class InvoiceNumbering:
    def __init__(self, prefix: str = "INV", padding: int = 6) -> None:
        self._prefix = prefix
        self._padding = padding
        self._counter = 0
        self._used: set = set()

    def next_number(self) -> str:
        self._counter += 1
        number = f"{self._prefix}-{self._counter:0{self._padding}d}"
        self._used.add(number)
        return number

    def is_valid(self, number: str) -> bool:
        return number in self._used

    def get_current(self) -> int:
        return self._counter

    def set_counter(self, value: int) -> None:
        self._counter = value

    def get_all_used(self) -> list:
        return sorted(self._used)

    def count(self) -> int:
        return len(self._used)

    def reset(self) -> int:
        n = self._counter
        self._counter = 0
        self._used.clear()
        return n
