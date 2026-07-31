"""Order domain model — imports the base entity via ``from .base``."""

from .base import BaseEntity


class OrderItem(BaseEntity):
    """A single order line."""

    def __init__(self, sku: str, qty: int) -> None:
        self.sku = sku
        self.qty = qty


class Order(BaseEntity):
    """An order with its items."""

    def __init__(self, order_id: str, customer: str, items: list[OrderItem],
                 ref: str = "") -> None:
        self.order_id = order_id
        self.customer = customer
        self.items = items
        self.ref = ref

    def total(self) -> float:
        return sum(item.qty * 10.0 for item in self.items)
