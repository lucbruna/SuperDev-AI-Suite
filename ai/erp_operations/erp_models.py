"""ERP Models — Core data models for ERP operations."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ProductStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"


class OrderStatus(Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class PaymentStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    PARTIAL = "partial"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class EmployeeStatus(Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"


class WorkflowStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


@dataclass
class Product:
    product_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    sku: str = ""
    category: str = ""
    price: float = 0.0
    cost: float = 0.0
    stock_quantity: int = 0
    min_stock: int = 0
    max_stock: int = 1000
    unit: str = "unit"
    status: ProductStatus = ProductStatus.ACTIVE
    supplier_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class StockMovement:
    movement_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    product_id: str = ""
    movement_type: str = "in"
    quantity: int = 0
    reference: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    notes: str = ""


@dataclass
class Order:
    order_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    customer_id: str = ""
    items: list[dict[str, Any]] = field(default_factory=list)
    total: float = 0.0
    status: OrderStatus = OrderStatus.DRAFT
    priority: OrderPriority = OrderPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    payment_status: PaymentStatus = PaymentStatus.PENDING
    notes: str = ""


@dataclass
class PurchaseOrder:
    po_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    supplier_id: str = ""
    items: list[dict[str, Any]] = field(default_factory=list)
    total: float = 0.0
    status: OrderStatus = OrderStatus.DRAFT
    expected_date: datetime | None = None
    created_at: datetime = field(default_factory=datetime.now)
    notes: str = ""


@dataclass
class Supplier:
    supplier_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    contact: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    rating: float = 0.0
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Employee:
    employee_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    department: str = ""
    position: str = ""
    email: str = ""
    phone: str = ""
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    hire_date: datetime = field(default_factory=datetime.now)
    salary: float = 0.0


@dataclass
class WorkOrder:
    work_order_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    product_id: str = ""
    quantity: int = 0
    status: OrderStatus = OrderStatus.DRAFT
    assigned_to: str = ""
    start_date: datetime | None = None
    end_date: datetime | None = None
    created_at: datetime = field(default_factory=datetime.now)
    notes: str = ""


@dataclass
class Delivery:
    delivery_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    order_id: str = ""
    origin: str = ""
    destination: str = ""
    status: OrderStatus = OrderStatus.DRAFT
    estimated_arrival: datetime | None = None
    actual_arrival: datetime | None = None
    tracking_number: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class WarehouseLocation:
    location_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    zone: str = ""
    aisle: str = ""
    shelf: str = ""
    capacity: int = 0
    current_stock: int = 0


@dataclass
class WorkflowApproval:
    approval_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    workflow_name: str = ""
    entity_type: str = ""
    entity_id: str = ""
    requested_by: str = ""
    approved_by: str = ""
    status: WorkflowStatus = WorkflowStatus.PENDING
    comments: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: datetime | None = None
