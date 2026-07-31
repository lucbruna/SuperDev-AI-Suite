"""Order service — depends on sibling packages via relative imports.

Uses ``from ..models.order`` and ``from ..utils.helpers`` (level-2) plus
``from .helpers`` (level-1) to exercise relative-import resolution.
"""

from ..models.order import Order, OrderItem
from ..utils.helpers import generate_id
from .helpers import build_order_id


class OrderService:
    """Creates orders."""

    def create_order(self, customer: str, items: list[dict]) -> Order:
        order_items = [OrderItem(sku=item["sku"], qty=item["qty"])
                       for item in items]
        return Order(order_id=build_order_id(), customer=customer,
                     items=order_items, ref=generate_id())
