"""Warehouse engine."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from .models import WarehouseZoneModel, Bin, PutAwayTask, PickTask, WarehouseZone, BinStatus


class WarehouseEngine:
    def __init__(self):
        self._zones: Dict[str, WarehouseZoneModel] = {}
        self._bins: Dict[str, Bin] = {}
        self._putaway_tasks: List[PutAwayTask] = []
        self._pick_tasks: List[PickTask] = []

    def add_zone(self, zone: WarehouseZoneModel) -> WarehouseZoneModel:
        self._zones[zone.zone_id] = zone
        return zone

    def get_zone(self, zone_id: str) -> Optional[WarehouseZoneModel]:
        return self._zones.get(zone_id)

    def add_bin(self, bin_obj: Bin) -> Bin:
        self._bins[bin_obj.bin_id] = bin_obj
        return bin_obj

    def get_bin(self, bin_id: str) -> Optional[Bin]:
        return self._bins.get(bin_id)

    def find_empty_bins(self, zone_id: Optional[str] = None) -> List[Bin]:
        bins = [b for b in self._bins.values() if b.status == BinStatus.EMPTY]
        if zone_id:
            bins = [b for b in bins if b.zone_id == zone_id]
        return bins

    def assign_product_to_bin(self, bin_id: str, product_id: str, quantity: int) -> bool:
        bin_obj = self._bins.get(bin_id)
        if not bin_obj:
            return False
        bin_obj.product_id = product_id
        bin_obj.quantity = quantity
        bin_obj.status = BinStatus.PARTIAL if quantity < bin_obj.max_capacity else BinStatus.FULL
        return True

    def create_putaway_task(self, task: PutAwayTask) -> PutAwayTask:
        self._putaway_tasks.append(task)
        return task

    def create_pick_task(self, task: PickTask) -> PickTask:
        self._pick_tasks.append(task)
        return task

    def get_pending_picks(self) -> List[PickTask]:
        return [t for t in self._pick_tasks if t.status == "pending"]

    def get_zone_utilization(self, zone_id: str) -> float:
        zone = self._zones.get(zone_id)
        return zone.utilization if zone else 0.0

    def get_stats(self) -> dict:
        bins = list(self._bins.values())
        return {
            "total_zones": len(self._zones),
            "total_bins": len(bins),
            "empty_bins": len([b for b in bins if b.status == BinStatus.EMPTY]),
            "full_bins": len([b for b in bins if b.status == BinStatus.FULL]),
            "putaway_tasks": len(self._putaway_tasks),
            "pick_tasks": len(self._pick_tasks),
        }
