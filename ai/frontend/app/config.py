"""
Frontend Configuration
"""
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Theme(Enum):
    """UI themes."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"
    HIGH_CONTRAST = "high_contrast"


class Language(Enum):
    """Interface languages."""
    EN = "en"
    PT = "pt"
    ES = "es"
    FR = "fr"
    DE = "de"
    ZH = "zh"
    JA = "ja"
    KO = "ko"


class LayoutMode(Enum):
    """Layout modes."""
    COMPACT = "compact"
    COMFORTABLE = "comfortable"
    SPACIOUS = "spacious"


@dataclass
class FrontendConfig:
    """Main frontend configuration."""
    app_name: str = "SuperDev AI Suite"
    version: str = "5.0.0"
    theme: Theme = Theme.DARK
    language: Language = Language.PT
    layout_mode: LayoutMode = LayoutMode.COMFORTABLE

    # API Configuration
    api_url: str = "http://localhost:8000"
    ws_url: str = "ws://localhost:8001"
    api_timeout: int = 30000

    # Auth Configuration
    auth_token_key: str = "superdev_token"
    refresh_token_key: str = "superdev_refresh"
    session_timeout: int = 3600

    # Feature Flags
    enable_ai_chat: bool = True
    enable_code_editor: bool = True
    enable_real_time: bool = True
    enable_analytics: bool = True
    enable_collaboration: bool = True
    enable_dark_mode: bool = True
    enable_accessibility: bool = True

    # UI Settings
    sidebar_width: int = 260
    header_height: int = 64
    footer_height: int = 48
    max_upload_size: int = 10 * 1024 * 1024  # 10MB

    # Editor Settings
    editor_font_size: int = 14
    editor_tab_size: int = 4
    editor_word_wrap: bool = False
    editor_minimap: bool = True
    editor_auto_save: bool = True

    # AI Settings
    ai_max_tokens: int = 4096
    ai_temperature: float = 0.7
    ai_streaming: bool = True

    # Dashboard Settings
    dashboard_refresh_interval: int = 5000
    dashboard_max_widgets: int = 50

    # Multi-tenant
    tenant_isolation: bool = True
    custom_branding: bool = True

    # Accessibility
    reduce_motion: bool = False
    high_contrast: bool = False
    screen_reader_mode: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "app_name": self.app_name,
            "version": self.version,
            "theme": self.theme.value,
            "language": self.language.value,
            "layout_mode": self.layout_mode.value,
            "api_url": self.api_url,
            "ws_url": self.ws_url,
            "enable_ai_chat": self.enable_ai_chat,
            "enable_code_editor": self.enable_code_editor,
            "enable_real_time": self.enable_real_time,
            "sidebar_width": self.sidebar_width,
            "header_height": self.header_height,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FrontendConfig":
        """Create from dictionary."""
        return cls(
            app_name=data.get("app_name", "SuperDev AI Suite"),
            version=data.get("version", "5.0.0"),
            theme=Theme(data.get("theme", "dark")),
            language=Language(data.get("language", "pt")),
            api_url=data.get("api_url", "http://localhost:8000"),
            ws_url=data.get("ws_url", "ws://localhost:8001"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "FrontendConfig":
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))

    def save(self, path: str) -> None:
        """Save config to file."""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "FrontendConfig":
        """Load config from file."""
        with open(path) as f:
            return cls.from_dict(json.load(f))


@dataclass
class TenantConfig:
    """Multi-tenant configuration."""
    tenant_id: str
    name: str
    domain: str | None = None
    logo_url: str | None = None
    primary_color: str = "#3B82F6"
    features: list[str] = field(default_factory=list)
    limits: dict[str, int] = field(default_factory=dict)
    is_active: bool = True

    def has_feature(self, feature: str) -> bool:
        """Check if tenant has feature enabled."""
        return feature in self.features or len(self.features) == 0

    def get_limit(self, resource: str) -> int:
        """Get resource limit for tenant."""
        return self.limits.get(resource, 100)


@dataclass
class FeatureFlag:
    """Feature flag configuration."""
    name: str
    enabled: bool = True
    percentage: int = 100
    allowed_tenants: list[str] = field(default_factory=list)
    allowed_roles: list[str] = field(default_factory=list)

    def is_enabled(self, tenant_id: str | None = None, role: str | None = None) -> bool:
        """Check if feature is enabled for tenant/role."""
        if not self.enabled:
            return False
        if self.allowed_tenants and tenant_id not in self.allowed_tenants:
            return False
        return not (self.allowed_roles and role not in self.allowed_roles)
