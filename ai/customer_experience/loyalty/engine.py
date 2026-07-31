"""Loyalty engine."""

import uuid
from datetime import datetime

from .models import (
    CustomerValue,
    LoyaltyAccount,
    LoyaltyAction,
    LoyaltyTransaction,
    Reward,
)


class LoyaltyEngine:
    def __init__(self, points_per_dollar: int = 10):
        self._accounts: dict[str, LoyaltyAccount] = {}
        self._transactions: dict[str, list[LoyaltyTransaction]] = {}
        self._rewards: dict[str, Reward] = {}
        self._customer_values: dict[str, CustomerValue] = {}
        self._points_per_dollar = points_per_dollar

    def get_or_create_account(self, customer_id: str) -> LoyaltyAccount:
        if customer_id not in self._accounts:
            self._accounts[customer_id] = LoyaltyAccount(customer_id=customer_id)
        return self._accounts[customer_id]

    def earn_points(self, customer_id: str, points: int, description: str = "") -> LoyaltyTransaction:
        account = self.get_or_create_account(customer_id)
        account.balance += points
        account.total_earned += points
        account.last_activity = datetime.now()
        tx = LoyaltyTransaction(
            transaction_id=str(uuid.uuid4())[:8],
            customer_id=customer_id,
            action=LoyaltyAction.EARN,
            points=points,
            balance=account.balance,
            description=description,
        )
        self._transactions.setdefault(customer_id, []).append(tx)
        return tx

    def earn_from_purchase(self, customer_id: str, amount: float) -> LoyaltyTransaction:
        points = int(amount * self._points_per_dollar)
        return self.earn_points(customer_id, points, f"Earned from purchase of {amount:.2f}")

    def redeem_points(self, customer_id: str, points: int, description: str = "") -> LoyaltyTransaction | None:
        account = self._accounts.get(customer_id)
        if not account or account.balance < points:
            return None
        account.balance -= points
        account.total_redeemed += points
        account.last_activity = datetime.now()
        tx = LoyaltyTransaction(
            transaction_id=str(uuid.uuid4())[:8],
            customer_id=customer_id,
            action=LoyaltyAction.REDEEM,
            points=points,
            balance=account.balance,
            description=description,
        )
        self._transactions.setdefault(customer_id, []).append(tx)
        return tx

    def get_balance(self, customer_id: str) -> int:
        account = self._accounts.get(customer_id)
        return account.balance if account else 0

    def add_reward(self, reward: Reward) -> Reward:
        self._rewards[reward.reward_id] = reward
        return reward

    def get_rewards(self) -> list[Reward]:
        return [r for r in self._rewards.values() if r.active]

    def get_transactions(self, customer_id: str) -> list[LoyaltyTransaction]:
        return self._transactions.get(customer_id, [])

    def calculate_customer_value(self, customer_id: str, total_spent: float = 0.0, orders: int = 0) -> CustomerValue:
        avg_order = total_spent / orders if orders > 0 else 0.0
        freq = orders / 12.0 if orders > 0 else 0.0
        cv = CustomerValue(
            customer_id=customer_id,
            lifetime_value=total_spent,
            avg_order_value=avg_order,
            purchase_frequency=freq,
            churn_risk=max(0.0, 1.0 - freq),
            clv_score=total_spent * freq,
        )
        self._customer_values[customer_id] = cv
        return cv

    def get_customer_value(self, customer_id: str) -> CustomerValue | None:
        return self._customer_values.get(customer_id)

    def update_tier(self, customer_id: str) -> str:
        account = self._accounts.get(customer_id)
        if not account:
            return "bronze"
        if account.total_earned >= 10000:
            account.tier = "diamond"
        elif account.total_earned >= 5000:
            account.tier = "platinum"
        elif account.total_earned >= 2000:
            account.tier = "gold"
        elif account.total_earned >= 500:
            account.tier = "silver"
        else:
            account.tier = "bronze"
        return account.tier
