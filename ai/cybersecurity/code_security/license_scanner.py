"""
License Compliance Scanner
"""
from dataclasses import dataclass
from enum import Enum


class LicenseCategory(Enum):
    PERMISSIVE = "permissive"
    WEAK_COPYLEFT = "weak_copyleft"
    STRONG_COPYLEFT = "strong_copyleft"
    PROPRIETARY = "proprietary"
    UNKNOWN = "unknown"


@dataclass
class LicenseInfo:
    name: str
    category: LicenseCategory
    spdx_id: str = ""
    url: str = ""
    osi_approved: bool = False
    risk_level: str = "low"


@dataclass
class ComponentLicense:
    component: str
    version: str
    license: str
    license_info: LicenseInfo | None = None
    compliant: bool = True


class LicenseScanner:
    def __init__(self):
        self.known_licenses: dict[str, LicenseInfo] = {
            "MIT": LicenseInfo("MIT", LicenseCategory.PERMISSIVE, "MIT", osi_approved=True),
            "Apache-2.0": LicenseInfo("Apache-2.0", LicenseCategory.PERMISSIVE, "Apache-2.0", osi_approved=True),
            "GPL-3.0": LicenseInfo("GPL-3.0", LicenseCategory.STRONG_COPYLEFT, "GPL-3.0-only", osi_approved=True),
            "LGPL-3.0": LicenseInfo("LGPL-3.0", LicenseCategory.WEAK_COPYLEFT, "LGPL-3.0-only", osi_approved=True),
            "BSD-3-Clause": LicenseInfo("BSD-3-Clause", LicenseCategory.PERMISSIVE, "BSD-3-Clause", osi_approved=True),
            "ISC": LicenseInfo("ISC", LicenseCategory.PERMISSIVE, "ISC", osi_approved=True),
            "AGPL-3.0": LicenseInfo("AGPL-3.0", LicenseCategory.STRONG_COPYLEFT, "AGPL-3.0-only", osi_approved=True),
        }
        self.scanned_components: list[ComponentLicense] = []
        self.blocked_licenses: set = {"AGPL-3.0"}

    def scan_component(self, component: str, version: str, license_name: str) -> ComponentLicense:
        lic_info = self.known_licenses.get(license_name)
        compliant = license_name not in self.blocked_licenses
        result = ComponentLicense(component=component, version=version, license=license_name, license_info=lic_info, compliant=compliant)
        self.scanned_components.append(result)
        return result

    def get_non_compliant(self) -> list[ComponentLicense]:
        return [c for c in self.scanned_components if not c.compliant]

    def get_by_category(self, category: LicenseCategory) -> list[ComponentLicense]:
        return [c for c in self.scanned_components if c.license_info and c.license_info.category == category]

    def add_license(self, info: LicenseInfo) -> None:
        self.known_licenses[info.name] = info

    def block_license(self, license_name: str) -> None:
        self.blocked_licenses.add(license_name)

    def unblock_license(self, license_name: str) -> bool:
        if license_name in self.blocked_licenses:
            self.blocked_licenses.remove(license_name)
            return True
        return False

    def get_summary(self) -> dict[str, int]:
        summary = {}
        for comp in self.scanned_components:
            summary[comp.license] = summary.get(comp.license, 0) + 1
        return summary

    def count(self) -> int:
        return len(self.scanned_components)
