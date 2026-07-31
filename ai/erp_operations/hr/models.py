"""HR models."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
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
    hire_date: Optional[datetime] = None
    salary: float = 0.0
    manager_id: str = ""
    email: str = ""
    phone: str = ""


@dataclass
class LeaveRequest:
    request_id: str
    employee_id: str = ""
    leave_type: LeaveType = LeaveType.ANNUAL
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
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
    processed_at: Optional[datetime] = None


@dataclass
class Department:
    department_id: str
    name: str = ""
    manager_id: str = ""
    budget: float = 0.0
    headcount: int = 0
    location: str = ""
