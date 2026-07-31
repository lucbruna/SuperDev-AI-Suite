"""HR engine."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from .models import Employee, LeaveRequest, PayrollRecord, Department, EmployeeStatus, LeaveType, LeaveStatus


class HREngine:
    def __init__(self):
        self._employees: Dict[str, Employee] = {}
        self._leave_requests: List[LeaveRequest] = []
        self._payroll: List[PayrollRecord] = []
        self._departments: Dict[str, Department] = {}

    def add_employee(self, employee: Employee) -> Employee:
        self._employees[employee.employee_id] = employee
        return employee

    def get_employee(self, employee_id: str) -> Optional[Employee]:
        return self._employees.get(employee_id)

    def update_employee_status(self, employee_id: str, status: EmployeeStatus) -> bool:
        emp = self._employees.get(employee_id)
        if not emp:
            return False
        emp.status = status
        return True

    def get_employees_by_department(self, department: str) -> List[Employee]:
        return [e for e in self._employees.values() if e.department == department]

    def submit_leave_request(self, request: LeaveRequest) -> LeaveRequest:
        self._leave_requests.append(request)
        return request

    def approve_leave(self, request_id: str, approved_by: str) -> bool:
        for r in self._leave_requests:
            if r.request_id == request_id:
                r.status = LeaveStatus.APPROVED
                r.approved_by = approved_by
                return True
        return False

    def get_leave_balance(self, employee_id: str, leave_type: LeaveType) -> int:
        approved = [r for r in self._leave_requests
                    if r.employee_id == employee_id and r.leave_type == leave_type and r.status == LeaveStatus.APPROVED]
        total_taken = sum(r.days for r in approved)
        allowances = {LeaveType.ANNUAL: 20, LeaveType.SICK: 10, LeaveType.PERSONAL: 5}
        limit = allowances.get(leave_type, 0)
        return max(0, limit - total_taken)

    def process_payroll(self, record: PayrollRecord) -> PayrollRecord:
        record.net_pay = record.base_salary + record.bonus - record.deductions
        record.status = "processed"
        record.processed_at = datetime.now()
        self._payroll.append(record)
        return record

    def add_department(self, dept: Department) -> Department:
        self._departments[dept.department_id] = dept
        return dept

    def get_department(self, dept_id: str) -> Optional[Department]:
        return self._departments.get(dept_id)

    def get_stats(self) -> dict:
        employees = list(self._employees.values())
        return {
            "total_employees": len(employees),
            "active": len([e for e in employees if e.status == EmployeeStatus.ACTIVE]),
            "departments": len(self._departments),
            "leave_requests": len(self._leave_requests),
            "payroll_records": len(self._payroll),
        }
