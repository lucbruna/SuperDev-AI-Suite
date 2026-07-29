from __future__ import annotations as __

import asyncio
from typing import Dict, List, Optional, Any

from .flag_rules import Flag, FlagRule, evaluate_flag


class FeatureFlagManager:
    def __init__(self) -> None:
        self._flags: Dict[str, Flag] = {}
        self._seed_flags()

    def _seed_flags(self) -> None:
        defaults = [
            Flag(
                name="new_dashboard",
                description="Enable the new dashboard UI",
                enabled=False,
                rules=[
                    FlagRule(type="plan_tier", values=["enterprise"]),
                    FlagRule(type="percentage", values=[10]),
                ],
                default_value=False,
            ),
            Flag(
                name="advanced_analytics",
                description="Enable advanced analytics features",
                enabled=True,
                rules=[
                    FlagRule(type="plan_tier", values=["pro", "enterprise"]),
                ],
                default_value=False,
            ),
            Flag(
                name="beta_api",
                description="Enable beta API endpoints",
                enabled=True,
                rules=[
                    FlagRule(type="percentage", values=[5]),
                ],
                default_value=False,
            ),
            Flag(
                name="audit_logs",
                description="Enable audit logging",
                enabled=True,
                rules=[
                    FlagRule(type="plan_tier", values=["pro", "enterprise"]),
                ],
                default_value=False,
            ),
            Flag(
                name="sso_enabled",
                description="Enable SSO authentication",
                enabled=True,
                rules=[
                    FlagRule(type="plan_tier", values=["enterprise"]),
                ],
                default_value=False,
            ),
        ]
        for flag in defaults:
            self._flags[flag.name] = flag

    async def is_enabled(
        self, flag_name: str, context: Optional[Dict[str, Any]] = None
    ) -> bool:
        await asyncio.sleep(0.01)
        flag = self._flags.get(flag_name)
        if not flag:
            return False
        return evaluate_flag(flag, context or {})

    async def get_flags(
        self, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        await asyncio.sleep(0.01)
        ctx = context or {}
        result: Dict[str, Any] = {}
        for name, flag in self._flags.items():
            result[name] = {
                "enabled": evaluate_flag(flag, ctx),
                "description": flag.description,
                "default_value": flag.default_value,
            }
        return result

    async def set_flag(
        self, flag_name: str, rules: List[Dict[str, Any]]
    ) -> Flag:
        await asyncio.sleep(0.01)
        flag_rules = [FlagRule(**r) for r in rules]

        if flag_name in self._flags:
            flag = self._flags[flag_name]
            flag.rules = flag_rules
        else:
            flag = Flag(
                name=flag_name,
                rules=flag_rules,
            )
            self._flags[flag_name] = flag

        return flag

    async def delete_flag(self, flag_name: str) -> bool:
        await asyncio.sleep(0.01)
        return self._flags.pop(flag_name, None) is not None

    async def toggle_flag(self, flag_name: str, enabled: bool) -> Flag | None:
        await asyncio.sleep(0.01)
        flag = self._flags.get(flag_name)
        if not flag:
            return None
        flag.enabled = enabled
        return flag
