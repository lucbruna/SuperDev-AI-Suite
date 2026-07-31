"""
Register Page
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class RegisterForm:
    name: str = ""
    email: str = ""
    password: str = ""
    confirm_password: str = ""
    company: str = ""
    accept_terms: bool = False


class RegisterPage:
    def __init__(self):
        self.form = RegisterForm()
        self.loading = False
        self.error: str | None = None
        self.step: int = 1

    def set_field(self, field: str, value: Any) -> None:
        if hasattr(self.form, field):
            setattr(self.form, field, value)

    def next_step(self) -> bool:
        if self.step < 3:
            self.step += 1
            return True
        return False

    def prev_step(self) -> bool:
        if self.step > 1:
            self.step -= 1
            return True
        return False

    def validate(self) -> bool:
        if not self.form.name or not self.form.email:
            self.error = "Name and email are required"
            return False
        if self.form.password != self.form.confirm_password:
            self.error = "Passwords do not match"
            return False
        return True

    def render(self) -> dict[str, Any]:
        return {"step": self.step, "loading": self.loading, "error": self.error}
