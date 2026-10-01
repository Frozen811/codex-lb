"""Build missing frontend assets for source installs, including Git installs."""

from __future__ import annotations

import runpy
from pathlib import Path

# Hatchling is installed in isolated PEP 517 build environments, not runtime.
from hatchling.builders.hooks.plugin.interface import BuildHookInterface  # ty: ignore[unresolved-import]


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict[str, object]) -> None:
        root = Path(self.root)
        helper = runpy.run_path(str(root / "scripts" / "build_dashboard.py"))
        helper["ensure_dashboard"](root)
