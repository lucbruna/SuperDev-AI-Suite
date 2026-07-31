"""ERP Factory — Factory for creating ERP components."""
from typing import Any

from .erp_models import (
    Delivery,
    Employee,
    Order,
    OrderPriority,
    OrderStatus,
    Product,
    ProductStatus,
    PurchaseOrder,
    Supplier,
    WorkOrder,
)


class ERPFactory:
    def __init__(self):
        self._templates: dict[str, dict[str, Any]] = {
            "standard_product": {"status": ProductStatus.ACTIVE, "unit": "unit"},
            "bulk_order": {"priority": OrderPriority.HIGH, "status": OrderStatus.DRAFT},
            "urgent_purchase": {"priority": OrderPriority.URGENT, "status": OrderStatus.DRAFT},
        }

    def create_product(self, name: str, sku: str = "", price: float = 0.0, **kwargs) -> Product:
        return Product(name=name, sku=sku, price=price, **kwargs)

    def create_order(self, customer_id: str, items: list | None = None, total: float = 0.0, **kwargs) -> Order:
        return Order(customer_id=customer_id, items=items or [], total=total, **kwargs)

    def create_purchase_order(self, supplier_id: str, items: list | None = None, total: float = 0.0, **kwargs) -> PurchaseOrder:
        return PurchaseOrder(supplier_id=supplier_id, items=items or [], total=total, **kwargs)

    def create_supplier(self, name: str, contact: str = "", **kwargs) -> Supplier:
        return Supplier(name=name, contact=contact, **kwargs)

    def create_employee(self, name: str, department: str = "", position: str = "", **kwargs) -> Employee:
        return Employee(name=name, department=department, position=position, **kwargs)

    def create_delivery(self, order_id: str, origin: str = "", destination: str = "", **kwargs) -> Delivery:
        return Delivery(order_id=order_id, origin=origin, destination=destination, **kwargs)

    def create_work_order(self, product_id: str, quantity: int = 0, **kwargs) -> WorkOrder:
        return WorkOrder(product_id=product_id, quantity=quantity, **kwargs)

    def register_template(self, name: str, template: dict[str, Any]) -> None:
        self._templates[name] = template

    def get_template(self, name: str) -> dict[str, Any] | None:
        return self._templates.get(name)

    def list_templates(self) -> list[str]:
        return list(self._templates.keys())
