#!/usr/bin/env bash
set -euo pipefail

echo "========================================================"
echo "  codex-lb (Hardened Community Edition)"
echo "  Web Dashboard: http://localhost:2455"
echo "========================================================"

if ! command -v uv >/dev/null 2>&1; then
    echo "[ERROR] 'uv' was not found in PATH."
    echo "Install uv by running:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

exec uv run codex-lb "$@"
