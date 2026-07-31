"""ERP Engine — Core ERP engine."""

from datetime import datetime
from typing import Any

from .erp_config import ERPConfig
from .erp_models import (
    Delivery,
    Employee,
    Order,
    OrderStatus,
    Product,
    PurchaseOrder,
    StockMovement,
    Supplier,
    WarehouseLocation,
    WorkflowApproval,
    WorkflowStatus,
    WorkOrder,
)


class ERPEngine:
    def __init__(self, config: ERPConfig | None = None):
        self._config = config or ERPConfig()
        self._products: dict[str, Product] = {}
        self._stock_movements: list[StockMovement] = []
        self._orders: dict[str, Order] = {}
        self._purchase_orders: dict[str, PurchaseOrder] = {}
        self._suppliers: dict[str, Supplier] = {}
        self._employees: dict[str, Employee] = {}
        self._deliveries: dict[str, Delivery] = {}
        self._work_orders: dict[str, WorkOrder] = {}
        self._locations: dict[str, WarehouseLocation] = {}
        self._approvals: list[WorkflowApproval] = []

    def add_product(self, product: Product) -> Product:
        self._products[product.product_id] = product
        return product

    def get_product(self, product_id: str) -> Product | None:
        return self._products.get(product_id)

    def list_products(self, category: str | None = None) -> list[Product]:
        products = list(self._products.values())
        if category:
            products = [p for p in products if p.category == category]
        return products

    def update_stock(self, product_id: str, quantity: int, movement_type: str, reference: str = "") -> bool:
        product = self._products.get(product_id)
        if not product:
            return False
        if movement_type == "in":
            product.stock_quantity += quantity
        elif movement_type == "out":
            if product.stock_quantity < quantity:
                return False
            product.stock_quantity -= quantity
        movement = StockMovement(
            product_id=product_id,
            movement_type=movement_type,
            quantity=quantity,
            reference=reference,
        )
        self._stock_movements.append(movement)
        return True

    def get_low_stock_products(self) -> list[Product]:
        return [p for p in self._products.values() if p.stock_quantity <= p.min_stock]

    def add_order(self, order: Order) -> Order:
        self._orders[order.order_id] = order
        return order

    def get_order(self, order_id: str) -> Order | None:
        return self._orders.get(order_id)

    def update_order_status(self, order_id: str, status: OrderStatus) -> bool:
        order = self._orders.get(order_id)
        if not order:
            return False
        order.status = status
        order.updated_at = datetime.now()
        return True

    def add_purchase_order(self, po: PurchaseOrder) -> PurchaseOrder:
        self._purchase_orders[po.po_id] = po
        return po

    def get_purchase_order(self, po_id: str) -> PurchaseOrder | None:
        return self._purchase_orders.get(po_id)

    def add_supplier(self, supplier: Supplier) -> Supplier:
        self._suppliers[supplier.supplier_id] = supplier
        return supplier

    def get_supplier(self, supplier_id: str) -> Supplier | None:
        return self._suppliers.get(supplier_id)

    def add_employee(self, employee: Employee) -> Employee:
        self._employees[employee.employee_id] = employee
        return employee

    def get_employee(self, employee_id: str) -> Employee | None:
        return self._employees.get(employee_id)

    def get_department_employees(self, department: str) -> list[Employee]:
        return [e for e in self._employees.values() if e.department == department]

    def add_delivery(self, delivery: Delivery) -> Delivery:
        self._deliveries[delivery.delivery_id] = delivery
        return delivery

    def get_delivery(self, delivery_id: str) -> Delivery | None:
        return self._deliveries.get(delivery_id)

    def add_work_order(self, wo: WorkOrder) -> WorkOrder:
        self._work_orders[wo.work_order_id] = wo
        return wo

    def get_work_order(self, wo_id: str) -> WorkOrder | None:
        return self._work_orders.get(wo_id)

    def add_location(self, location: WarehouseLocation) -> WarehouseLocation:
        self._locations[location.location_id] = location
        return location

    def get_location(self, location_id: str) -> WarehouseLocation | None:
        return self._locations.get(location_id)

    def add_approval(self, approval: WorkflowApproval) -> WorkflowApproval:
        self._approvals.append(approval)
        return approval

    def get_approvals(self, status: WorkflowStatus | None = None) -> list[WorkflowApproval]:
        approvals = self._approvals
        if status:
            approvals = [a for a in approvals if a.status == status]
        return approvals

    def get_stats(self) -> dict[str, Any]:
        return {
            "products": len(self._products),
            "orders": len(self._orders),
            "purchase_orders": len(self._purchase_orders),
            "suppliers": len(self._suppliers),
            "employees": len(self._employees),
            "deliveries": len(self._deliveries),
            "work_orders": len(self._work_orders),
            "low_stock": len(self.get_low_stock_products()),
        }
