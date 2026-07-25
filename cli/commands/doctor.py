import os
import platform
import shutil
import subprocess
import sys

import typer


def _check_python():
    version = sys.version
    major, minor, _ = sys.version_info
    ok = major >= 3 and minor >= 11
    return ok, f"Python {version}", "3.11+ required" if not ok else None


def _check_node():
    path = shutil.which("node")
    if not path:
        return False, "Node.js: NOT FOUND", "Required for frontend development"
    result = subprocess.run(["node", "--version"], capture_output=True, text=True)
    version = result.stdout.strip() if result.returncode == 0 else "unknown"
    ok = result.returncode == 0
    return ok, f"Node.js {version}", None if ok else "Failed to get version"


def _check_docker():
    path = shutil.which("docker")
    if not path:
        return False, "Docker: NOT FOUND", "Required for containerized execution"
    result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
    version = result.stdout.strip() if result.returncode == 0 else "unknown"
    ok = result.returncode == 0
    return ok, f"Docker {version}", None if ok else "Docker daemon not running"


def _check_git():
    path = shutil.which("git")
    if not path:
        return False, "Git: NOT FOUND", "Required for version control"
    result = subprocess.run(["git", "--version"], capture_output=True, text=True)
    version = result.stdout.strip() if result.returncode == 0 else "unknown"
    return True, f"Git {version}", None


def _check_system():
    system = platform.system()
    release = platform.release()
    return True, f"OS: {system} {release}", None


def doctor():
    checks = [_check_python(), _check_node(), _check_docker(), _check_git(), _check_system()]

    typer.echo("SuperDev Doctor - System Diagnostics")
    typer.echo("=" * 50)

    all_ok = True
    for ok, label, issue in checks:
        status = "\u2705" if ok else "\u274c"
        typer.echo(f"  {status}  {label}")
        if not ok and issue:
            typer.echo(f"       \u2139\ufe0f  {issue}")
            all_ok = False

    typer.echo("=" * 50)
    if all_ok:
        typer.echo("\u2705  All checks passed! System is ready for SuperDev.")
    else:
        typer.echo("\u26a0\ufe0f  Some issues found. Please resolve them before continuing.")