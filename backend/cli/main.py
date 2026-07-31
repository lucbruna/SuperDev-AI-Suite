#!/usr/bin/env python3
"""SuperDev CLI - Full command line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def cmd_init(args):
    """Initialize a new SuperDev project."""
    print("🔧 Initializing SuperDev project...")
    project_dir = Path(args.path or ".")
    project_dir.mkdir(parents=True, exist_ok=True)

    # Create standard directories
    dirs = [
        "backend",
        "frontend",
        "ai",
        "plugins",
        "tests",
        "docs",
        "infrastructure",
        "scripts",
    ]
    for d in dirs:
        (project_dir / d).mkdir(exist_ok=True)
        (project_dir / d / "__init__.py").touch(exist_ok=True)

    # Create .env template
    env_file = project_dir / ".env.example"
    env_file.write_text("""# SuperDev AI Suite Configuration
APP_ENVIRONMENT=development
APP_DEBUG=true
JWT_SECRET_KEY=change-me-in-production
DATABASE_URL=postgresql+asyncpg://superdev:superdev@localhost:5432/superdev
REDIS_HOST=localhost
REDIS_PORT=6379
CORS_ALLOW_ORIGINS=["http://localhost:3000"]
""")

    # Create pyproject.toml template
    pyproject = project_dir / "pyproject.toml"
    pyproject.write_text("""[project]
name = "superdev-ai-suite"
version = "5.0.0"
description = "Enterprise AI Suite"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn>=0.20.0",
    "sqlalchemy>=2.0.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.6",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.20.0",
    "httpx>=0.24.0",
    "ruff>=0.1.0",
]
""")

    print(f"✅ Project initialized at {project_dir}")
    print("   Run 'superdev doctor' to check system health")


def cmd_doctor(args):
    """Check system health."""
    print("🏥 System Health Check")
    print("=" * 40)

    checks = []

    # Python version
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    py_ok = sys.version_info >= (3, 11)
    checks.append(("Python", py_ver, py_ok))

    # Check key packages
    for pkg, label in [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("sqlalchemy", "SQLAlchemy"),
        ("pydantic", "Pydantic"),
        ("jose", "python-jose"),
        ("passlib", "passlib"),
    ]:
        try:
            mod = __import__(pkg)
            ver = getattr(mod, "__version__", "installed")
            checks.append((label, ver, True))
        except ImportError:
            checks.append((label, "NOT INSTALLED", False))

    # Check optional packages
    for pkg, label in [
        ("redis", "Redis"),
        ("asyncpg", "asyncpg"),
        ("aiosmtplib", "aiosmtplib"),
        ("openpyxl", "openpyxl"),
        ("pyotp", "pyotp (MFA)"),
    ]:
        try:
            mod = __import__(pkg)
            ver = getattr(mod, "__version__", "installed")
            checks.append((label, ver, True))
        except ImportError:
            checks.append((label, "NOT INSTALLED (optional)", False))

    all_ok = True
    for name, value, ok in checks:
        status_icon = "✅" if ok else "❌"
        if not ok and "optional" not in value.lower():
            all_ok = False
        print(f"  {status_icon} {name}: {value}")

    print("=" * 40)
    if all_ok:
        print("✅ All required dependencies installed")
    else:
        print("⚠️  Some required dependencies are missing")


def cmd_status(args):
    """Show system status."""
    print("📊 SuperDev AI Suite v5.0.0")
    print("=" * 40)

    # Check config
    env_file = Path(".env")
    if env_file.exists():
        print("  ✅ Configuration: .env found")
    else:
        print("  ⚠️  Configuration: .env not found (using defaults)")

    # Check database connectivity
    try:
        from backend.config import config

        print(f"  📦 Database: {config.database.url.split('@')[-1] if '@' in config.database.url else 'configured'}")
        print(f"  🔴 Redis: {config.redis.host}:{config.redis.port}")
    except Exception:
        print("  ⚠️  Config not loadable")

    # Check modules
    modules = [
        ("backend.auth", "Authentication"),
        ("backend.websocket", "WebSockets"),
        ("backend.cache", "Cache"),
        ("backend.scheduler", "Scheduler"),
        ("backend.notifications", "Notifications"),
        ("backend.plugins", "Plugin System"),
        ("backend.backup", "Backup/Recovery"),
        ("backend.export_import", "Export/Import"),
        ("backend.i18n", "i18n"),
        ("backend.search", "Full-Text Search"),
        ("backend.security", "SSO/Security"),
        ("backend.events", "Event Bus"),
    ]

    print("\n📦 Modules:")
    for mod_path, label in modules:
        try:
            __import__(mod_path)
            print(f"  ✅ {label}")
        except ImportError:
            print(f"  ❌ {label}")


def cmd_backup(args):
    """Manage backups."""
    print("💾 Backup Manager")
    # Placeholder for CLI backup commands
    print("  Use the API endpoints for backup operations:")
    print("  POST /api/v1/backup/database  - Backup database")
    print("  POST /api/v1/backup/files     - Backup files")
    print("  POST /api/v1/backup/full      - Full backup")


def cmd_i18n(args):
    """Manage translations."""
    print("🌍 Internationalization")
    try:
        from backend.i18n.translations import i18n

        stats = i18n.get_stats()
        print(f"  Current locale: {stats['current_locale']}")
        print(f"  Supported: {', '.join(stats['supported_locales'])}")
        for locale, count in stats["translation_counts"].items():
            print(f"  {locale}: {count} translations")
    except Exception as e:
        print(f"  Error loading i18n: {e}")


def cmd_search(args):
    """Search operations."""
    print("🔍 Full-Text Search")
    try:
        from backend.search.full_text_search import full_text_search

        stats = full_text_search.get_stats()
        print(f"  Documents indexed: {stats['total_documents']}")
        print(f"  Terms in index: {stats['total_terms']}")
        for dtype, count in stats["by_type"].items():
            if count > 0:
                print(f"  {dtype}: {count}")
    except Exception as e:
        print(f"  Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        prog="superdev",
        description="SuperDev AI Suite CLI",
    )
    parser.add_argument("--version", action="version", version="5.0.0")

    subparsers = parser.add_subparsers(dest="command")

    # init
    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("path", nargs="?", default=".", help="Project path")

    # doctor
    subparsers.add_parser("doctor", help="Check system health")

    # status
    subparsers.add_parser("status", help="Show system status")

    # backup
    subparsers.add_parser("backup", help="Manage backups")

    # i18n
    subparsers.add_parser("i18n", help="Manage translations")

    # search
    subparsers.add_parser("search", help="Search operations")

    args = parser.parse_args()

    commands = {
        "init": cmd_init,
        "doctor": cmd_doctor,
        "status": cmd_status,
        "backup": cmd_backup,
        "i18n": cmd_i18n,
        "search": cmd_search,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
