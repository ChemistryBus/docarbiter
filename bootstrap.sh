#!/usr/bin/env bash
# bootstrap.sh — clone docarbiter and run its installer.
#
# For non-CLI users:
#   curl -fsSL https://raw.githubusercontent.com/ChemistryBus/docarbiter/main/bootstrap.sh | bash
#
# Safer: download, read, then run:
#   curl -fsSL .../bootstrap.sh -o /tmp/docarbiter-bootstrap.sh
#   bash /tmp/docarbiter-bootstrap.sh
#
# Pass installer flags after `bash -s --`, e.g.:
#   curl ... | bash -s -- --skills-only
set -euo pipefail

REPO_URL="${DOCARBITER_REPO_URL:-https://github.com/ChemistryBus/docarbiter.git}"
DEST="${DOCARBITER_HOME:-$HOME/.local/share/docarbiter}"

command -v git >/dev/null 2>&1 || {
  echo "[bootstrap] git is required to clone docarbiter" >&2
  exit 1
}

if [ -d "$DEST/.git" ]; then
  echo "[bootstrap] updating $DEST"
  git -C "$DEST" pull --ff-only
else
  echo "[bootstrap] cloning into $DEST"
  mkdir -p "$(dirname "$DEST")"
  git clone --depth 1 "$REPO_URL" "$DEST"
fi

exec "$DEST/scripts/install.sh" "$@"
