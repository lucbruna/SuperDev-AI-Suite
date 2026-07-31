"""Licenses subsystem generator."""
import os

BASE = r'C:\Users\tomga\OneDrive\Desktop\super_dev_suite\SuperDev\ai\enterprise\licenses'

def w(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)

w('license_engine.py', '''"""License engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class LicenseEngine:
    def __init__(self) -> None:
        self._licenses: Dict[str, Dict[str, Any]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def create(self, org_id: str, plan_id: str, key: str, max_activations: int = 1) -> Dict[str, Any]:
        import uuid
        lic_id = str(uuid.uuid4())[:8]
        lic = {"id": lic_id, "org_id": org_id, "plan_id": plan_id, "key": key, "status": "active", "max_activations": max_activations, "activations": 0, "created_at": time.time()}
        self._licenses[lic_id] = lic
        return lic
    def get(self, lic_id: str) -> Optional[Dict[str, Any]]:
        return self._licenses.get(lic_id)
    def get_by_key(self, key: str) -> Optional[Dict[str, Any]]:
        for lic in self._licenses.values():
            if lic["key"] == key:
                return lic
        return None
    def revoke(self, lic_id: str) -> bool:
        lic = self._licenses.get(lic_id)
        if lic:
            lic["status"] = "revoked"
            return True
        return False
    def list_by_org(self, org_id: str) -> List[Dict[str, Any]]:
        return [l for l in self._licenses.values() if l["org_id"] == org_id]
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._licenses.values())
    def count(self) -> int:
        return len(self._licenses)
    def is_running(self) -> bool:
        return self._started
''')

w('license_manager.py', '''"""License manager."""
from __future__ import annotations
from typing import Any, Dict, List

class LicenseManager:
    def __init__(self) -> None:
        self._assignments: Dict[str, str] = {}
    def assign(self, license_id: str, org_id: str) -> bool:
        self._assignments[license_id] = org_id
        return True
    def unassign(self, license_id: str) -> bool:
        if license_id in self._assignments:
            del self._assignments[license_id]
            return True
        return False
    def get_org(self, license_id: str) -> str:
        return self._assignments.get(license_id, "")
    def list_by_org(self, org_id: str) -> List[str]:
        return [lid for lid, oid in self._assignments.items() if oid == org_id]
    def count(self) -> int:
        return len(self._assignments)
    def has_license(self, org_id: str) -> bool:
        return org_id in self._assignments.values()
    def list_all(self) -> Dict[str, str]:
        return dict(self._assignments)
''')

w('key_generator.py', '''"""License key generator."""
from __future__ import annotations
import random, string

class LicenseKeyGenerator:
    def __init__(self, prefix: str = "SD", length: int = 32) -> None:
        self._prefix = prefix
        self._length = length
        self._generated: list = []
    def generate(self) -> str:
        chars = string.ascii_uppercase + string.digits
        key_body = ''.join(random.choices(chars, k=self._length))
        key = f"{self._prefix}-{key_body[:8]}-{key_body[8:16]}-{key_body[16:24]}-{key_body[24:]}"
        self._generated.append(key)
        return key
    def generate_batch(self, count: int) -> list:
        return [self.generate() for _ in range(count)]
    def is_valid_format(self, key: str) -> bool:
        parts = key.split('-')
        return len(parts) == 5 and parts[0] == self._prefix
    def get_generated_count(self) -> int:
        return len(self._generated)
    def list_keys(self) -> list:
        return list(self._generated)
''')

w('activation.py', '''"""License activation."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class LicenseActivation:
    def __init__(self) -> None:
        self._activations: Dict[str, List[Dict[str, Any]]] = {}
    def activate(self, license_id: str, machine_id: str = "", user_id: str = "") -> Dict[str, Any]:
        entry = {"license_id": license_id, "machine_id": machine_id, "user_id": user_id, "activated_at": time.time()}
        self._activations.setdefault(license_id, []).append(entry)
        return entry
    def deactivate(self, license_id: str, machine_id: str = "") -> bool:
        activations = self._activations.get(license_id, [])
        if machine_id:
            self._activations[license_id] = [a for a in activations if a.get("machine_id") != machine_id]
        else:
            self._activations.pop(license_id, None)
        return True
    def get_activations(self, license_id: str) -> List[Dict[str, Any]]:
        return list(self._activations.get(license_id, []))
    def activation_count(self, license_id: str) -> int:
        return len(self._activations.get(license_id, []))
    def is_active(self, license_id: str) -> bool:
        return self.activation_count(license_id) > 0
    def list_all(self) -> Dict[str, List[Dict[str, Any]]]:
        return dict(self._activations)
''')

w('validation.py', '''"""License validation."""
from __future__ import annotations
from typing import Any, Dict
import time

class LicenseValidator:
    def __init__(self) -> None:
        self._rules: Dict[str, Any] = {}
    def set_rules(self, license_id: str, max_activations: int = 1, expires_at: float = 0, allowed_plans: list = None) -> None:
        self._rules[license_id] = {"max_activations": max_activations, "expires_at": expires_at, "allowed_plans": allowed_plans or []}
    def validate(self, license: Dict[str, Any], current_activations: int) -> Dict[str, Any]:
        errors = []
        rules = self._rules.get(license.get("id", ""), {})
        if license.get("status") != "active":
            errors.append("license_not_active")
        if rules.get("expires_at") and time.time() > rules["expires_at"]:
            errors.append("license_expired")
        if current_activations >= rules.get("max_activations", 1):
            errors.append("max_activations_reached")
        if rules.get("allowed_plans") and license.get("plan_id") not in rules["allowed_plans"]:
            errors.append("plan_not_allowed")
        return {"valid": len(errors) == 0, "errors": errors}
    def list_rules(self) -> Dict[str, Any]:
        return dict(self._rules)
    def remove_rules(self, license_id: str) -> bool:
        if license_id in self._rules:
            del self._rules[license_id]
            return True
        return False
''')

w('expiration.py', '''"""License expiration."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class LicenseExpiration:
    def __init__(self) -> None:
        self._expirations: Dict[str, float] = {}
        self._warnings: Dict[str, List[Dict[str, Any]]] = {}
    def set_expiration(self, license_id: str, expires_at: float) -> None:
        self._expirations[license_id] = expires_at
    def get_expiration(self, license_id: str) -> float:
        return self._expirations.get(license_id, 0.0)
    def is_expired(self, license_id: str) -> bool:
        exp = self._expirations.get(license_id)
        return exp is not None and time.time() > exp
    def days_until_expiration(self, license_id: str) -> float:
        exp = self._expirations.get(license_id, 0)
        if exp == 0:
            return float('inf')
        return max(0, (exp - time.time()) / 86400)
    def add_warning(self, license_id: str, days_before: int, message: str) -> None:
        self._warnings.setdefault(license_id, []).append({"days_before": days_before, "message": message})
    def get_warnings(self, license_id: str) -> List[Dict[str, Any]]:
        return self._warnings.get(license_id, [])
    def get_expiring_soon(self, days: int = 30) -> List[str]:
        cutoff = time.time() + days * 86400
        return [lid for lid, exp in self._expirations.items() if 0 < exp <= cutoff]
    def list_all(self) -> Dict[str, float]:
        return dict(self._expirations)
''')

w('transfer.py', '''"""License transfer."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class LicenseTransfer:
    def __init__(self, allow_transfer: bool = True) -> None:
        self._allow_transfer = allow_transfer
        self._transfers: List[Dict[str, Any]] = []
    def transfer(self, license_id: str, from_org: str, to_org: str) -> Dict[str, Any]:
        if not self._allow_transfer:
            return {"error": "transfer_not_allowed"}
        entry = {"license_id": license_id, "from_org": from_org, "to_org": to_org, "transferred_at": time.time()}
        self._transfers.append(entry)
        return entry
    def list_transfers(self) -> List[Dict[str, Any]]:
        return list(self._transfers)
    def get_by_license(self, license_id: str) -> List[Dict[str, Any]]:
        return [t for t in self._transfers if t["license_id"] == license_id]
    def count(self) -> int:
        return len(self._transfers)
    def is_allowed(self) -> bool:
        return self._allow_transfer
    def set_allow_transfer(self, allowed: bool) -> None:
        self._allow_transfer = allowed
''')

w('__init__.py', '''"""Licenses subsystem."""
from .license_engine import LicenseEngine
from .license_manager import LicenseManager
from .key_generator import LicenseKeyGenerator
from .activation import LicenseActivation
from .validation import LicenseValidator
from .expiration import LicenseExpiration
from .transfer import LicenseTransfer

__all__ = [
    "LicenseEngine", "LicenseManager", "LicenseKeyGenerator",
    "LicenseActivation", "LicenseValidator", "LicenseExpiration", "LicenseTransfer"
]
''')

print("licenses/: 8 files created")
