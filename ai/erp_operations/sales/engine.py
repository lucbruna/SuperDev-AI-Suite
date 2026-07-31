"""Sales engine."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from .models import SalesOrder, Quotation, SalesTarget, Commission, SalesOrderStatus, QuotationStatus


class SalesEngine:
    def __init__(self):
        self._orders: Dict[str, SalesOrder] = {}
        self._quotations: Dict[str, Quotation] = {}
        self._targets: Dict[str, SalesTarget] = {}
        self._commissions: List[Commission] = []

    def create_order(self, order: SalesOrder) -> SalesOrder:
        self._orders[order.order_id] = order
        return order

    def get_order(self, order_id: str) -> Optional[SalesOrder]:
        return self._orders.get(order_id)

    def update_order_status(self, order_id: str, status: SalesOrderStatus) -> bool:
        order = self._orders.get(order_id)
        if not order:
            return False
        order.status = status
        return True

    def create_quotation(self, quotation: Quotation) -> Quotation:
        self._quotations[quotation.quotation_id] = quotation
        return quotation

    def get_quotation(self, quotation_id: str) -> Optional[Quotation]:
        return self._quotations.get(quotation_id)

    def accept_quotation(self, quotation_id: str) -> bool:
        q = self._quotations.get(quotation_id)
        if not q:
            return False
        q.status = QuotationStatus.ACCEPTED
        return True

    def set_target(self, target: SalesTarget) -> SalesTarget:
        self._targets[target.target_id] = target
        return target

    def get_target(self, target_id: str) -> Optional[SalesTarget]:
        return self._targets.get(target_id)

    def get_rep_targets(self, sales_rep: str) -> List[SalesTarget]:
        return [t for t in self._targets.values() if t.sales_rep == sales_rep]

    def add_commission(self, commission: Commission) -> Commission:
        self._commissions.append(commission)
        return commission

    def get_commissions(self, sales_rep: str, period: Optional[str] = None) -> List[Commission]:
        comms = [c for c in self._commissions if c.sales_rep == sales_rep]
        if period:
            comms = [c for c in comms if c.period == period]
        return comms

    def get_stats(self) -> dict:
        orders = list(self._orders.values())
        total_revenue = sum(o.total for o in orders)
        return {
            "total_orders": len(orders),
            "total_revenue": total_revenue,
            "quotations": len(self._quotations),
            "targets": len(self._targets),
        }
