"""Smoke readiness and bundled dashboard assets using isolated release storage."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import socket
import subprocess
import tempfile
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from scripts.release_versions import parse_version


def smoke_http(base_url: str, process: subprocess.Popen | None = None) -> None:
    for _ in range(90):
        if process is not None and process.poll() is not None:
            raise ValueError(f"release server exited before readiness: {process.returncode}")
        try:
            with urlopen(f"{base_url}/health/ready", timeout=2) as response:
                if response.status == 200:
                    break
        except (URLError, OSError):
            pass
        time.sleep(1)
    else:
        raise ValueError("release readiness smoke timed out")
    with urlopen(base_url + "/", timeout=10) as response:
        html = response.read().decode()
        if response.status != 200 or "text/html" not in response.headers.get("Content-Type", ""):
            raise ValueError("dashboard HTML is unavailable")
    assets = re.findall(r'(?:src|href)="(/assets/[^"?#]+\.(?:js|css))"', html)
    if not any(asset.endswith(".js") for asset in assets) or not any(asset.endswith(".css") for asset in assets):
        raise ValueError("dashboard HTML does not reference JavaScript and CSS")
    for asset in assets:
        with urlopen(base_url + asset, timeout=10) as response:
            if response.status != 200 or not response.read() or "text/html" in response.headers.get("Content-Type", ""):
                raise ValueError(f"dashboard asset unavailable: {asset}")
    print("release readiness, dashboard HTML, JavaScript and CSS passed")


@contextmanager
def smoke_directory() -> Iterator[str]:
    directory = tempfile.TemporaryDirectory(prefix="codex-lb-smoke-")
    try:
        yield directory.name
    finally:
        # Descendant handles can still be closing after taskkill returns.
        # Wait for sharing locks; propagate other errors and persistent locks.
        deadline = time.monotonic() + 15
        while True:
            try:
                directory.cleanup()
                break
            except PermissionError as error:
                if getattr(error, "winerror", None) != 32 or time.monotonic() >= deadline:
                    raise
                time.sleep(0.05)


def smoke_package(python: Path, version: str) -> None:
    with smoke_directory() as temporary:
        root = Path(temporary)
        env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("CODEX_LB_")
            and key
            not in {
                "PYTHONPATH",
                "PYTHONHOME",
                "GITHUB_TOKEN",
                "GH_TOKEN",
                "GITHUB_OUTPUT",
                "PORT",
                "HOST",
                "WEB_CONCURRENCY",
            }
        }
        env.update(
            {
                "CODEX_LB_DATA_DIR": str(root),
                "CODEX_LB_DATABASE_URL": f"sqlite+aiosqlite:///{(root / 'smoke.db').as_posix()}",
                "CODEX_LB_ENCRYPTION_KEY_FILE": str(root / "encryption.key"),
                "CODEX_LB_ENV_FILE": str(root / "absent.env"),
            }
        )
        actual = subprocess.check_output(
            [str(python), "-I", "-c", "import app; print(app.__version__)"], cwd=root, env=env, text=True
        ).strip()
        if actual != version:
            raise ValueError(f"installed runtime version mismatch: {actual!r}")
        installed_source = json.loads(
            subprocess.check_output(
                [
                    str(python),
                    "-I",
                    "-c",
                    "import app, pathlib, hashlib, json; root=pathlib.Path(app.__file__).parent; "
                    "print(json.dumps({p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() "
                    "for p in root.rglob('*.py')}))",
                ],
                cwd=root,
                env=env,
                text=True,
            )
        )
        source_root = Path(__file__).resolve().parents[1] / "app"
        expected_source = {
            path.relative_to(source_root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in source_root.rglob("*.py")
        }
        if installed_source != expected_source:
            raise ValueError("installed application source differs from checkout")
        metadata_version = subprocess.check_output(
            [str(python), "-I", "-c", "from importlib.metadata import version; print(version('codex-lb'))"],
            cwd=root,
            env=env,
            text=True,
        ).strip()
        if metadata_version != parse_version(version).pypi_version:
            raise ValueError(f"installed distribution version mismatch: {metadata_version!r}")
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        with (root / "server.log").open("w+", encoding="utf-8") as log:
            process = subprocess.Popen(
                [str(python), "-I", "-m", "app.cli", "--host", "127.0.0.1", "--port", str(port)],
                cwd=root,
                env=env,
                stdout=log,
                stderr=log,
            )
            try:
                smoke_http(f"http://127.0.0.1:{port}", process)
            except Exception:
                log.seek(0)
                print(log.read())
                raise
            finally:
                if os.name == "nt" and process.poll() is None:
                    # uv's Windows venv launcher owns a child interpreter.
                    subprocess.run(
                        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                elif process.poll() is None:
                    process.terminate()
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--base-url")
    mode.add_argument("--python", type=Path)
    parser.add_argument("--version")
    args = parser.parse_args()
    if args.python:
        if not args.version:
            parser.error("--python requires --version")
        smoke_package(args.python.resolve(), args.version)
    else:
        smoke_http(args.base_url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
