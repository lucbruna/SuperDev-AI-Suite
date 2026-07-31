"""
Login Page
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class LoginForm:
    email: str = ""
    password: str = ""
    remember_me: bool = False


class LoginPage:
    def __init__(self):
        self.form = LoginForm()
        self.loading = False
        self.error: str | None = None
        self.on_submit: Callable | None = None

    def set_email(self, email: str) -> None:
        self.form.email = email

    def set_password(self, password: str) -> None:
        self.form.password = password

    def toggle_remember(self) -> None:
        self.form.remember_me = not self.form.remember_me

    def submit(self) -> bool:
        if not self.form.email or not self.form.password:
            self.error = "Email and password are required"
            return False
        self.loading = True
        self.error = None
        if self.on_submit:
            self.on_submit(self.form)
        return True

    def set_error(self, error: str) -> None:
        self.error = error
        self.loading = False

    def render(self) -> dict[str, Any]:
        return {
            "form": {"email": self.form.email, "rememberMe": self.form.remember_me},
            "loading": self.loading,
            "error": self.error,
        }
