"""
Frontend Application Providers
"""
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ThemeMode(Enum):
    """Theme modes."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


@dataclass
class ThemeColors:
    """Theme color palette."""
    primary: str = "#3B82F6"
    secondary: str = "#6B7280"
    success: str = "#10B981"
    warning: str = "#F59E0B"
    danger: str = "#EF4444"
    background: str = "#111827"
    surface: str = "#1F2937"
    text: str = "#F9FAFB"
    text_secondary: str = "#9CA3AF"
    border: str = "#374151"


@dataclass
class Theme:
    """Theme configuration."""
    name: str
    mode: ThemeMode
    colors: ThemeColors
    fonts: dict[str, str] = field(default_factory=dict)
    spacing: dict[str, int] = field(default_factory=dict)
    borderRadius: dict[str, str] = field(default_factory=dict)
    shadows: dict[str, str] = field(default_factory=dict)

    @classmethod
    def dark(cls) -> "Theme":
        """Create dark theme."""
        return cls(
            name="dark",
            mode=ThemeMode.DARK,
            colors=ThemeColors(),
            fonts={
                "body": "'Inter', sans-serif",
                "heading": "'Inter', sans-serif",
                "mono": "'JetBrains Mono', monospace",
            },
            spacing={
                "xs": 4,
                "sm": 8,
                "md": 16,
                "lg": 24,
                "xl": 32,
                "2xl": 48,
            },
            borderRadius={
                "sm": "4px",
                "md": "8px",
                "lg": "12px",
                "xl": "16px",
                "full": "9999px",
            },
            shadows={
                "sm": "0 1px 2px rgba(0,0,0,0.3)",
                "md": "0 4px 6px rgba(0,0,0,0.3)",
                "lg": "0 10px 15px rgba(0,0,0,0.3)",
                "xl": "0 20px 25px rgba(0,0,0,0.3)",
            }
        )

    @classmethod
    def light(cls) -> "Theme":
        """Create light theme."""
        return cls(
            name="light",
            mode=ThemeMode.LIGHT,
            colors=ThemeColors(
                background="#F9FAFB",
                surface="#FFFFFF",
                text="#111827",
                text_secondary="#6B7280",
                border="#E5E7EB",
            ),
            fonts={
                "body": "'Inter', sans-serif",
                "heading": "'Inter', sans-serif",
                "mono": "'JetBrains Mono', monospace",
            }
        )


class ThemeProvider:
    """Theme provider for the application."""

    def __init__(self, initial_theme: Theme | None = None):
        self.current_theme = initial_theme or Theme.dark()
        self.themes: dict[str, Theme] = {
            "dark": Theme.dark(),
            "light": Theme.light(),
        }
        self.listeners: list[Callable] = []
        self.storage_key = "superdev_theme"

    def get_theme(self) -> Theme:
        """Get current theme."""
        return self.current_theme

    def set_theme(self, theme_name: str) -> None:
        """Set theme by name."""
        if theme_name in self.themes:
            self.current_theme = self.themes[theme_name]
            self._persist_theme()
            self._notify_listeners()

    def toggle_theme(self) -> None:
        """Toggle between dark and light themes."""
        if self.current_theme.mode == ThemeMode.DARK:
            self.set_theme("light")
        else:
            self.set_theme("dark")

    def register_theme(self, name: str, theme: Theme) -> None:
        """Register a custom theme."""
        self.themes[name] = theme

    def get_color(self, color_name: str) -> str:
        """Get a color from current theme."""
        return getattr(self.current_theme.colors, color_name, "#000000")

    def on_theme_change(self, callback: Callable) -> None:
        """Register theme change listener."""
        self.listeners.append(callback)

    def _persist_theme(self) -> None:
        """Persist theme preference."""
        # Would use localStorage in browser
        pass

    def _load_persisted_theme(self) -> None:
        """Load persisted theme preference."""
        # Would use localStorage in browser
        pass

    def _notify_listeners(self) -> None:
        """Notify theme change listeners."""
        for callback in self.listeners:
            callback(self.current_theme)


class AppProvider:
    """Main application provider."""

    def __init__(self):
        self.theme_provider = ThemeProvider()
        self.auth_provider = AuthProvider()
        self.api_provider = APIProvider()
        self.ws_provider = WebSocketProvider()
        self.notification_provider = NotificationProvider()
        self.i18n_provider = I18nProvider()
        self.store_provider = StoreProvider()

    def initialize(self, config: dict[str, Any] | None = None) -> None:
        """Initialize all providers."""
        config = config or {}
        self.theme_provider.set_theme(config.get("theme", "dark"))
        self.i18n_provider.set_locale(config.get("language", "pt"))

    def get_theme_provider(self) -> ThemeProvider:
        """Get theme provider."""
        return self.theme_provider

    def get_auth_provider(self) -> "AuthProvider":
        """Get auth provider."""
        return self.auth_provider

    def get_api_provider(self) -> "APIProvider":
        """Get API provider."""
        return self.api_provider


class AuthProvider:
    """Authentication provider."""

    def __init__(self):
        self.user = None
        self.isAuthenticated = False
        self.token = None
        self.listeners: list[Callable] = []

    def login(self, credentials: dict[str, str]) -> bool:
        """Login with credentials."""
        # Placeholder
        return True

    def logout(self) -> None:
        """Logout user."""
        self.user = None
        self.isAuthenticated = False
        self.token = None

    def get_user(self) -> Any | None:
        """Get current user."""
        return self.user

    def on_auth_change(self, callback: Callable) -> None:
        """Register auth change listener."""
        self.listeners.append(callback)


class APIProvider:
    """API provider."""

    def __init__(self):
        self.base_url = ""
        self.headers: dict[str, str] = {}

    def set_base_url(self, url: str) -> None:
        """Set API base URL."""
        self.base_url = url

    def set_token(self, token: str) -> None:
        """Set auth token."""
        self.headers["Authorization"] = f"Bearer {token}"

    def request(self, method: str, endpoint: str, data: Any = None) -> Any:
        """Make API request."""
        # Placeholder
        return {"success": True, "data": data}


class WebSocketProvider:
    """WebSocket provider."""

    def __init__(self):
        self.connected = False
        self.url = ""

    def connect(self, url: str) -> None:
        """Connect to WebSocket."""
        self.url = url
        self.connected = True

    def disconnect(self) -> None:
        """Disconnect from WebSocket."""
        self.connected = False

    def send(self, event: str, data: Any) -> None:
        """Send message."""
        pass


class NotificationProvider:
    """Notification provider."""

    def __init__(self):
        self.notifications: list[dict] = []

    def show(self, message: str, type: str = "info") -> None:
        """Show notification."""
        self.notifications.append({"message": message, "type": type})

    def success(self, message: str) -> None:
        """Show success notification."""
        self.show(message, "success")

    def error(self, message: str) -> None:
        """Show error notification."""
        self.show(message, "error")


class I18nProvider:
    """Internationalization provider."""

    def __init__(self):
        self.locale = "pt"
        self.translations: dict[str, dict[str, str]] = {}
        self.fallback_locale = "en"

    def set_locale(self, locale: str) -> None:
        """Set current locale."""
        self.locale = locale

    def t(self, key: str, params: dict[str, str] | None = None) -> str:
        """Translate a key."""
        translations = self.translations.get(self.locale, {})
        if key in translations:
            text = translations[key]
        else:
            translations = self.translations.get(self.fallback_locale, {})
            text = translations.get(key, key)

        if params:
            for k, v in params.items():
                text = text.replace(f'{{{{{k}}}}}', v)
        return text

    def add_translations(self, locale: str, translations: dict[str, str]) -> None:
        """Add translations for a locale."""
        if locale not in self.translations:
            self.translations[locale] = {}
        self.translations[locale].update(translations)


class StoreProvider:
    """State store provider."""

    def __init__(self):
        self.stores: dict[str, Any] = {}

    def register(self, name: str, store: Any) -> None:
        """Register a store."""
        self.stores[name] = store

    def get(self, name: str) -> Any:
        """Get a store by name."""
        return self.stores.get(name)
