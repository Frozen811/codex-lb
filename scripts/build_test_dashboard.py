"""Reuse local test assets only when their build inputs still match."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from pathlib import Path

from scripts.build_dashboard import dashboard_complete


def source_digest(root: Path) -> str:
    frontend = root / "frontend"
    inputs = [path for directory in ("src", "public") for path in (frontend / directory).rglob("*") if path.is_file()]
    inputs.extend(
        path for path in frontend.iterdir() if path.is_file() and path.suffix in {".ts", ".json", ".html", ".lock"}
    )
    digest = hashlib.sha256()
    for path in sorted(inputs):
        digest.update(path.relative_to(frontend).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="store_true", help="record inputs after an explicit frontend build")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    stamp = root / ".pytest_cache/dashboard-source.sha256"
    digest = source_digest(root)
    if not args.record:
        if dashboard_complete(root) and stamp.is_file() and stamp.read_text().strip() == digest:
            print("Reusing current dashboard build")
            return
        frontend = root / "frontend"
        subprocess.run(["bun", "install", "--frozen-lockfile"], cwd=frontend, check=True)
        subprocess.run(["bun", "--bun", "run", "build"], cwd=frontend, check=True)
    if not dashboard_complete(root):
        raise RuntimeError("Dashboard build is incomplete")
    stamp.parent.mkdir(parents=True, exist_ok=True)
    stamp.write_text(digest + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
