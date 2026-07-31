"""Network manager."""
from __future__ import annotations

from typing import Any


class NetworkManager:
    def __init__(self) -> None:
        self._networks: dict[str, dict[str, Any]] = {}
        self._rules: list[dict[str, Any]] = []
    def create_network(self, name: str, cidr: str = "10.0.0.0/16") -> dict[str, Any]:
        network = {"name": name, "cidr": cidr, "subnets": [], "status": "active"}
        self._networks[name] = network
        return network
    def add_subnet(self, network_name: str, subnet_name: str, cidr: str) -> bool:
        if network_name not in self._networks:
            return False
        self._networks[network_name]["subnets"].append({"name": subnet_name, "cidr": cidr})
        return True
    def add_rule(self, name: str, source: str, destination: str, port: int, protocol: str = "tcp") -> dict[str, Any]:
        rule = {"name": name, "source": source, "destination": destination, "port": port, "protocol": protocol}
        self._rules.append(rule)
        return rule
    def check_access(self, source: str, destination: str, port: int) -> bool:
        return any(r["source"] == source and r["destination"] == destination and r["port"] == port for r in self._rules)
    def get_network(self, name: str) -> dict[str, Any]:
        return self._networks.get(name, {"error": "not_found"})
    def list_networks(self) -> list[dict[str, Any]]:
        return list(self._networks.values())
    def list_rules(self) -> list[dict[str, Any]]:
        return self._rules
    def count(self) -> int:
        return len(self._networks)
