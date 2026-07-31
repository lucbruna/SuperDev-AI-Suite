"""Logistics engine."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from .models import Shipment, Route, Carrier, DeliveryProof, ShipmentStatus, CarrierType


class LogisticsEngine:
    def __init__(self):
        self._shipments: Dict[str, Shipment] = {}
        self._routes: Dict[str, Route] = {}
        self._carriers: Dict[str, Carrier] = {}
        self._proofs: List[DeliveryProof] = []

    def create_shipment(self, shipment: Shipment) -> Shipment:
        self._shipments[shipment.shipment_id] = shipment
        return shipment

    def get_shipment(self, shipment_id: str) -> Optional[Shipment]:
        return self._shipments.get(shipment_id)

    def update_shipment_status(self, shipment_id: str, status: ShipmentStatus) -> bool:
        s = self._shipments.get(shipment_id)
        if not s:
            return False
        s.status = status
        if status == ShipmentStatus.DELIVERED:
            s.actual_delivery = datetime.now()
        return True

    def add_route(self, route: Route) -> Route:
        self._routes[route.route_id] = route
        return route

    def get_route(self, route_id: str) -> Optional[Route]:
        return self._routes.get(route_id)

    def find_routes(self, origin: str, destination: str) -> List[Route]:
        return [r for r in self._routes.values() if r.origin == origin and r.destination == destination]

    def add_carrier(self, carrier: Carrier) -> Carrier:
        self._carriers[carrier.carrier_id] = carrier
        return carrier

    def get_carrier(self, carrier_id: str) -> Optional[Carrier]:
        return self._carriers.get(carrier_id)

    def get_best_carrier(self, weight: float, carrier_type: Optional[CarrierType] = None) -> Optional[Carrier]:
        candidates = [c for c in self._carriers.values() if c.active and c.max_weight >= weight]
        if carrier_type:
            candidates = [c for c in candidates if c.carrier_type == carrier_type]
        if not candidates:
            return None
        return min(candidates, key=lambda c: c.cost_per_km)

    def add_delivery_proof(self, proof: DeliveryProof) -> DeliveryProof:
        self._proofs.append(proof)
        return proof

    def get_proof(self, shipment_id: str) -> Optional[DeliveryProof]:
        for p in self._proofs:
            if p.shipment_id == shipment_id:
                return p
        return None

    def get_stats(self) -> dict:
        shipments = list(self._shipments.values())
        delivered = [s for s in shipments if s.status == ShipmentStatus.DELIVERED]
        return {
            "total_shipments": len(shipments),
            "delivered": len(delivered),
            "in_transit": len([s for s in shipments if s.status == ShipmentStatus.IN_TRANSIT]),
            "carriers": len(self._carriers),
            "routes": len(self._routes),
        }
