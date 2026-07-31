"""Purchases engine."""
import uuid

from .models import PriceComparison, PurchaseOrder, PurchaseOrderStatus


class PurchasesEngine:
    def __init__(self):
        self._orders: dict[str, PurchaseOrder] = {}
        self._comparisons: list[PriceComparison] = []

    def create_order(self, order: PurchaseOrder) -> PurchaseOrder:
        self._orders[order.po_id] = order
        return order

    def get_order(self, po_id: str) -> PurchaseOrder | None:
        return self._orders.get(po_id)

    def approve_order(self, po_id: str, approved_by: str) -> bool:
        order = self._orders.get(po_id)
        if not order:
            return False
        order.status = PurchaseOrderStatus.APPROVED
        order.approved_by = approved_by
        return True

    def update_status(self, po_id: str, status: PurchaseOrderStatus) -> bool:
        order = self._orders.get(po_id)
        if not order:
            return False
        order.status = status
        return True

    def get_orders_by_supplier(self, supplier_id: str) -> list[PurchaseOrder]:
        return [o for o in self._orders.values() if o.supplier_id == supplier_id]

    def compare_prices(self, product_id: str, supplier_prices: dict[str, float]) -> PriceComparison:
        if not supplier_prices:
            return PriceComparison(comparison_id=str(uuid.uuid4())[:8], product_id=product_id)
        best_supplier = min(supplier_prices, key=supplier_prices.get)
        best_price = supplier_prices[best_supplier]
        prices_sorted = sorted(supplier_prices.values())
        savings = prices_sorted[-1] - best_price if len(prices_sorted) > 1 else 0.0
        comp = PriceComparison(
            comparison_id=str(uuid.uuid4())[:8],
            product_id=product_id,
            prices=supplier_prices,
            best_supplier=best_supplier,
            best_price=best_price,
            savings=savings,
        )
        self._comparisons.append(comp)
        return comp

    def get_stats(self) -> dict:
        orders = list(self._orders.values())
        total = sum(o.total for o in orders)
        return {"total_orders": len(orders), "total_spend": total, "comparisons": len(self._comparisons)}
