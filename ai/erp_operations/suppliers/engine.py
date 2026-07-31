"""Supplier engine."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from .models import Supplier, SupplierContract, SupplierPerformance, SupplierStatus, SupplierCategory


class SuppliersEngine:
    def __init__(self):
        self._suppliers: Dict[str, Supplier] = {}
        self._contracts: Dict[str, SupplierContract] = {}
        self._performance: List[SupplierPerformance] = []

    def add_supplier(self, supplier: Supplier) -> Supplier:
        self._suppliers[supplier.supplier_id] = supplier
        return supplier

    def get_supplier(self, supplier_id: str) -> Optional[Supplier]:
        return self._suppliers.get(supplier_id)

    def update_status(self, supplier_id: str, status: SupplierStatus) -> bool:
        supplier = self._suppliers.get(supplier_id)
        if not supplier:
            return False
        supplier.status = status
        return True

    def add_contract(self, contract: SupplierContract) -> SupplierContract:
        self._contracts[contract.contract_id] = contract
        return contract

    def get_supplier_contracts(self, supplier_id: str) -> List[SupplierContract]:
        return [c for c in self._contracts.values() if c.supplier_id == supplier_id]

    def add_performance(self, perf: SupplierPerformance) -> SupplierPerformance:
        perf.calculate_overall()
        self._performance.append(perf)
        return perf

    def get_supplier_performance(self, supplier_id: str) -> List[SupplierPerformance]:
        return [p for p in self._performance if p.supplier_id == supplier_id]

    def rate_supplier(self, supplier_id: str, rating: float) -> bool:
        supplier = self._suppliers.get(supplier_id)
        if not supplier:
            return False
        supplier.rating = max(0.0, min(5.0, rating))
        return True

    def get_top_suppliers(self, limit: int = 5) -> List[Supplier]:
        active = [s for s in self._suppliers.values() if s.status == SupplierStatus.ACTIVE]
        return sorted(active, key=lambda s: s.rating, reverse=True)[:limit]

    def get_stats(self) -> dict:
        suppliers = list(self._suppliers.values())
        return {
            "total_suppliers": len(suppliers),
            "active": len([s for s in suppliers if s.status == SupplierStatus.ACTIVE]),
            "contracts": len(self._contracts),
            "avg_rating": sum(s.rating for s in suppliers) / len(suppliers) if suppliers else 0.0,
        }
