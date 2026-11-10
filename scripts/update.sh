#!/usr/bin/env bash
# update.sh — pull the docarbiter repo and refresh registered skills/wrappers.
# It does not install Python packages; use install.sh --profile core for that.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$REPO_ROOT"

echo "[update] repo: $REPO_ROOT"
git pull --ff-only

# Re-register the skill and wrappers. Extra args pass through, e.g.
#   ./scripts/update.sh --force --skill-mode dir
exec "$REPO_ROOT/scripts/install.sh" --skills-only "$@"
