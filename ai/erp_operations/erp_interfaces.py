"""ERP Interfaces — Protocol interfaces for ERP operations."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from .erp_models import Product, Order, PurchaseOrder, Supplier, Employee, Delivery


class InventoryInterface(ABC):
    @abstractmethod
    def add_product(self, product: Product) -> Product:
        pass

    @abstractmethod
    def get_product(self, product_id: str) -> Optional[Product]:
        pass

    @abstractmethod
    def update_stock(self, product_id: str, quantity: int, movement_type: str) -> bool:
        pass

    @abstractmethod
    def get_low_stock_products(self) -> List[Product]:
        pass


class SalesInterface(ABC):
    @abstractmethod
    def create_order(self, order: Order) -> Order:
        pass

    @abstractmethod
    def get_order(self, order_id: str) -> Optional[Order]:
        pass

    @abstractmethod
    def update_status(self, order_id: str, status: str) -> bool:
        pass


class PurchaseInterface(ABC):
    @abstractmethod
    def create_purchase_order(self, po: PurchaseOrder) -> PurchaseOrder:
        pass

    @abstractmethod
    def get_purchase_order(self, po_id: str) -> Optional[PurchaseOrder]:
        pass

    @abstractmethod
    def approve_purchase(self, po_id: str) -> bool:
        pass


class SupplierInterface(ABC):
    @abstractmethod
    def add_supplier(self, supplier: Supplier) -> Supplier:
        pass

    @abstractmethod
    def get_supplier(self, supplier_id: str) -> Optional[Supplier]:
        pass

    @abstractmethod
    def rate_supplier(self, supplier_id: str, rating: float) -> bool:
        pass


class ProductionInterface(ABC):
    @abstractmethod
    def create_work_order(self, work_order: Any) -> Any:
        pass

    @abstractmethod
    def get_work_order(self, work_order_id: str) -> Optional[Any]:
        pass

    @abstractmethod
    def update_progress(self, work_order_id: str, progress: float) -> bool:
        pass


class LogisticsInterface(ABC):
    @abstractmethod
    def create_delivery(self, delivery: Delivery) -> Delivery:
        pass

    @abstractmethod
    def track_delivery(self, delivery_id: str) -> Optional[Delivery]:
        pass

    @abstractmethod
    def optimize_route(self, deliveries: List[str]) -> List[str]:
        pass


class HRInterface(ABC):
    @abstractmethod
    def add_employee(self, employee: Employee) -> Employee:
        pass

    @abstractmethod
    def get_employee(self, employee_id: str) -> Optional[Employee]:
        pass

    @abstractmethod
    def get_department_employees(self, department: str) -> List[Employee]:
        pass


class WorkflowInterface(ABC):
    @abstractmethod
    def submit_for_approval(self, entity_type: str, entity_id: str, requested_by: str) -> Any:
        pass

    @abstractmethod
    def approve(self, approval_id: str, approved_by: str) -> bool:
        pass

    @abstractmethod
    def reject(self, approval_id: str, comments: str) -> bool:
        pass
