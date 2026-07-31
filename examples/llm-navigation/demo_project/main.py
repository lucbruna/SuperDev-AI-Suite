"""Demo project entry point — imports services and utils.

The imports below create real edges in the dependency graph so the
LLM-navigation example can walk from this file into its dependencies.
"""

from services.order_service import OrderService
from utils.helpers import format_currency


def run() -> str:
    """Create an order and return a formatted total."""
    service = OrderService()
    order = service.create_order(customer="acme", items=[{"sku": "A1", "qty": 2}])
    return format_currency(order.total())
