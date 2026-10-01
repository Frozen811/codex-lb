"""Ensure source packages include the dashboard before Hatch builds them."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlsplit


def dashboard_complete(root: Path) -> bool:
    static = root / "app" / "static"
    index = static / "index.html"
    if not index.is_file():
        return False
    references = re.findall(r"(?:src|href)=[\"\']([^\"\']+)[\"\']", index.read_text(encoding="utf-8"))
    assets = [urlsplit(reference).path.lstrip("/") for reference in references]
    assets = [asset for asset in assets if asset.startswith("assets/") and asset.endswith((".js", ".css"))]
    if not all(any(asset.endswith(suffix) for asset in assets) for suffix in (".js", ".css")):
        return False
    for asset in assets:
        path = (static / asset).resolve()
        if not path.is_relative_to(static.resolve()) or not path.is_file() or not path.stat().st_size:
            return False
    return True


def ensure_dashboard(root: Path) -> None:
    if dashboard_complete(root):
        return
    frontend = root / "frontend"
    package = json.loads((frontend / "package.json").read_text(encoding="utf-8"))
    manager = package["packageManager"]
    if not isinstance(manager, str) or not manager.startswith("bun@"):
        raise RuntimeError("frontend/package.json must pin Bun via packageManager")
    expected = manager.removeprefix("bun@")
    bun = shutil.which("bun")
    guidance = (
        f"Install {manager} to build from source, or install a fork release wheel with prebuilt dashboard assets."
    )
    if bun is None:
        raise RuntimeError(f"Dashboard assets are missing and Bun is unavailable. {guidance}")
    actual = subprocess.check_output([bun, "--version"], text=True, timeout=10).strip()
    if actual != expected:
        raise RuntimeError(f"Dashboard source build needs {manager}; found Bun {actual}. {guidance}")
    subprocess.run([bun, "install", "--frozen-lockfile"], cwd=frontend, check=True, timeout=600)
    subprocess.run([bun, "run", "build"], cwd=frontend, check=True, timeout=600)
    if not dashboard_complete(root):
        raise RuntimeError("Frontend build did not produce complete dashboard HTML/JavaScript/CSS assets")
