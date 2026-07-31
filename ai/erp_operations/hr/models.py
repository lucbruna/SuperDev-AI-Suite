"""HR models."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class EmployeeStatus(Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"


class LeaveType(Enum):
    ANNUAL = "annual"
    SICK = "sick"
    PERSONAL = "personal"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    UNPAID = "unpaid"


class LeaveStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class Employee:
    employee_id: str
    name: str = ""
    department: str = ""
    position: str = ""
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    hire_date: datetime | None = None
    salary: float = 0.0
    manager_id: str = ""
    email: str = ""
    phone: str = ""


@dataclass
class LeaveRequest:
    request_id: str
    employee_id: str = ""
    leave_type: LeaveType = LeaveType.ANNUAL
    start_date: datetime | None = None
    end_date: datetime | None = None
    days: int = 0
    status: LeaveStatus = LeaveStatus.PENDING
    approved_by: str = ""
    reason: str = ""


@dataclass
class PayrollRecord:
    record_id: str
    employee_id: str = ""
    period: str = ""
    base_salary: float = 0.0
    bonus: float = 0.0
    deductions: float = 0.0
    net_pay: float = 0.0
    status: str = "pending"
    processed_at: datetime | None = None


@dataclass
class Department:
    department_id: str
    name: str = ""
    manager_id: str = ""
    budget: float = 0.0
    headcount: int = 0
    location: str = ""
