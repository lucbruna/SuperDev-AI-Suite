#!/usr/bin/env bash
# install_mantis_hooks.sh — enables the Mantis fast security check as a git
# post-commit hook so it runs automatically after every commit.
#
# The hook body lives VERSIONED at .githooks/post-commit (ships with the repo);
# this script simply points git at it via `core.hooksPath` and makes it
# executable, plus cleans up any legacy copy from .git/hooks/.
#
# Usage:
#   bash scripts/install_mantis_hooks.sh            # install (default)
#   bash scripts/install_mantis_hooks.sh --status   # show current hook state
#   bash scripts/install_mantis_hooks.sh --remove   # remove the hook
#
# Opt out per commit with:  SKIP_MANTIS=1 git commit

set -u

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "[mantis-hook] error: not inside a git repository" >&2
  exit 1
}

versioned_hook="$repo_root/.githooks/post-commit"
legacy_hook="$repo_root/.git/hooks/post-commit"
runner="$repo_root/run_mantis.py"
harness="$repo_root/scripts/mantis_pipeline.py"

# ── status: report whether the hook is installed and runnable ──────────────
status_hook() {
  echo "[mantis-hook] current state of this clone:"
  echo "  repository        : $repo_root"
  printf "  core.hooksPath    : "
  if cur="$(git config core.hooksPath)"; then echo "$cur"; else echo "(unset)"; fi
  printf "  .githooks/ tracked: "
  if git ls-files --error-unmatch .githooks/post-commit >/dev/null 2>&1; then
    echo "yes (versioned in the repo)"
  else
    echo "NO — hook not tracked, clones won't receive it!"
  fi
  printf "  hook file         : "
  if [ -f "$versioned_hook" ]; then
    if [ -x "$versioned_hook" ]; then
      echo "present + executable"
    else
      echo "present but NOT executable (run install)"
    fi
  else
    echo "MISSING ($versioned_hook)"
  fi
  printf "  runner            : "
  [ -f "$runner" ] && echo "present ($runner)" || echo "MISSING ($runner)"
  printf "  harness           : "
  [ -f "$harness" ] && echo "present ($harness)" || echo "MISSING ($harness)"
  if [ "$(git config core.hooksPath 2>/dev/null)" = ".githooks" ] \
    && [ -x "$versioned_hook" ] \
    && [ -f "$runner" ] \
    && [ -f "$harness" ]; then
    echo ""
    echo "  ✅ Mantis post-commit hook is INSTALLED and will run after every commit."
  else
    echo ""
    echo "  ⚠  Hook is NOT fully installed. Run:  bash scripts/install_mantis_hooks.sh"
  fi
  exit 0
}

# ── remove: unset hooksPath and drop any legacy copy ───────────────────────
remove_hook() {
  git config --unset core.hooksPath 2>/dev/null && \
    echo "[mantis-hook] unset core.hooksPath (post-commit hook disabled)"
  if [ -f "$legacy_hook" ]; then
    rm -f "$legacy_hook"
    echo "[mantis-hook] removed legacy copy $legacy_hook"
  fi
  echo "[mantis-hook] Mantis post-commit hook removed."
  exit 0
}

case "${1:-}" in
  --status|--check|status|check)
    status_hook
    ;;
  --remove|--uninstall|remove|uninstall)
    remove_hook
    ;;
  --help|-h|help)
    echo "Usage: bash scripts/install_mantis_hooks.sh [--status|--remove]"
    exit 0
    ;;
esac

# ── install (default) ──────────────────────────────────────────────────────
if [ ! -f "$versioned_hook" ]; then
  echo "[mantis-hook] error: versioned hook not found at $versioned_hook" >&2
  exit 1
fi

chmod +x "$versioned_hook"

# Enable git to run hooks from the versioned .githooks/ directory.
if ! git config core.hooksPath .githooks; then
  echo "[mantis-hook] error: failed to set core.hooksPath" >&2
  exit 1
fi

# Remove any legacy copy from a previous installation method so the hook does
# not run twice (core.hooksPath ignores .git/hooks, but be tidy anyway).
if [ -f "$legacy_hook" ]; then
  backup="${legacy_hook}.bak.$(date +%s)"
  cp "$legacy_hook" "$backup"
  rm -f "$legacy_hook"
  echo "[mantis-hook] moved legacy hook to $backup (core.hooksPath is now authoritative)"
fi

# WARNING: core.hooksPath makes git ignore .git/hooks/ ENTIRELY. If the
# developer has personal hooks there, they would silently stop running.
active=0
for f in "$repo_root"/.git/hooks/*; do
  case "$(basename "$f")" in
    *.sample|post-commit*) ;;        # samples, our legacy copy + backups
    README) ;;                       # non-hook
    *) [ -f "$f" ] && [ -x "$f" ] && active=$((active + 1)) ;;
  esac
done
if [ "$active" -gt 0 ]; then
  echo "[mantis-hook] NOTE: core.hooksPath disables other .git/hooks/ hooks ($active active)."
  echo "[mantis-hook] Move them into .githooks/ or remove this hook if you rely on them."
fi

# Post-install dependency check — the hook silently exits when these are
# missing, so fail loudly here instead of surprising the developer later.
missing=0
[ -f "$runner" ]   || { echo "[mantis-hook] WARNING: $runner missing — hook will no-op until it exists." >&2; missing=1; }
[ -f "$harness" ]  || { echo "[mantis-hook] WARNING: $harness missing — hook will no-op until it exists." >&2; missing=1; }

echo "[mantis-hook] installed post-commit hook: $versioned_hook (via core.hooksPath)"
echo "[mantis-hook] Mantis will now run its fast security check after every commit."
echo "[mantis-hook] verify anytime with:  bash scripts/install_mantis_hooks.sh --status"
echo "[mantis-hook] skip per commit with:  SKIP_MANTIS=1 git commit"
echo "[mantis-hook] remove with:           bash scripts/install_mantis_hooks.sh --remove"
exit "$missing"
