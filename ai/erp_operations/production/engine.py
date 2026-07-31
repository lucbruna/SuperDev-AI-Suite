"""Production engine."""
from .models import BOM, ProductionLine, ProductionOrder, ProductionStatus, QualityCheck


class ProductionEngine:
    def __init__(self):
        self._orders: dict[str, ProductionOrder] = {}
        self._lines: dict[str, ProductionLine] = {}
        self._quality_checks: list[QualityCheck] = []
        self._boms: dict[str, BOM] = {}

    def create_order(self, order: ProductionOrder) -> ProductionOrder:
        self._orders[order.order_id] = order
        return order

    def get_order(self, order_id: str) -> ProductionOrder | None:
        return self._orders.get(order_id)

    def update_order_status(self, order_id: str, status: ProductionStatus) -> bool:
        order = self._orders.get(order_id)
        if not order:
            return False
        order.status = status
        return True

    def add_line(self, line: ProductionLine) -> ProductionLine:
        self._lines[line.line_id] = line
        return line

    def get_line(self, line_id: str) -> ProductionLine | None:
        return self._lines.get(line_id)

    def get_available_lines(self) -> list[ProductionLine]:
        return [l for l in self._lines.values() if l.status == "available" and l.utilization < 100]

    def assign_order_to_line(self, order_id: str, line_id: str) -> bool:
        order = self._orders.get(order_id)
        line = self._lines.get(line_id)
        if not order or not line:
            return False
        order.assigned_line = line_id
        line.current_load += 1
        return True

    def add_quality_check(self, check: QualityCheck) -> QualityCheck:
        self._quality_checks.append(check)
        return check

    def get_quality_checks(self, order_id: str | None = None) -> list[QualityCheck]:
        if order_id:
            return [c for c in self._quality_checks if c.order_id == order_id]
        return list(self._quality_checks)

    def add_bom(self, bom: BOM) -> BOM:
        self._boms[bom.bom_id] = bom
        return bom

    def get_bom(self, bom_id: str) -> BOM | None:
        return self._boms.get(bom_id)

    def get_stats(self) -> dict:
        orders = list(self._orders.values())
        lines = list(self._lines.values())
        return {
            "total_orders": len(orders),
            "in_progress": len([o for o in orders if o.status == ProductionStatus.IN_PROGRESS]),
            "completed": len([o for o in orders if o.status == ProductionStatus.COMPLETED]),
            "production_lines": len(lines),
            "avg_efficiency": sum(l.efficiency for l in lines) / len(lines) if lines else 0.0,
            "quality_checks": len(self._quality_checks),
        }
