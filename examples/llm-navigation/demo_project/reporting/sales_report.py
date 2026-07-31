"""Sales reporting — imports OrderService via ``from ..services...``.

A level-2 relative import that must resolve back to the order_service module
(a *dependent* / reverse edge in the navigation graph).
"""

from ..services.order_service import OrderService


class SalesReport:
    """Builds a report from the order service."""

    def __init__(self) -> None:
        self.service = OrderService()

    def headline(self) -> str:
        return f"orders created via {self.service.__class__.__name__}"
