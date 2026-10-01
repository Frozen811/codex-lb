"""Prepare the dashboard before starting the CLI from a source checkout."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.build_dashboard import ensure_dashboard


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    if not any(argument in {"-h", "--help"} for argument in sys.argv[1:]):
        try:
            ensure_dashboard(root)
        except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
            print(f"Source startup failed: {exc}", file=sys.stderr)
            raise SystemExit(1) from None
    from app.cli import main as cli_main

    sys.argv[0] = "codex-lb"
    cli_main()


if __name__ == "__main__":
    main()
