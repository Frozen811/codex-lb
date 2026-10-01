"""Verify built archives against release version, frontend and application source."""

from __future__ import annotations

import argparse
import hashlib
import tarfile
import zipfile
from email import message_from_bytes
from pathlib import Path

from scripts.release_versions import assert_project_versions, parse_tag


def verify_contents(contents: dict[str, bytes], metadata_path: str, root: Path, version: str) -> None:
    metadata = message_from_bytes(contents[metadata_path])
    if metadata["Name"] != "codex-lb" or metadata["Version"] != version:
        raise ValueError("artifact metadata does not match the release")
    expected_source = {path.relative_to(root).as_posix(): path.read_bytes() for path in (root / "app").rglob("*.py")}
    packaged_source = {
        name: content for name, content in contents.items() if name.startswith("app/") and name.endswith(".py")
    }
    if packaged_source != expected_source:
        raise ValueError("packaged application source differs from checkout")
    assets = {name: content for name, content in contents.items() if name.startswith("app/static/")}
    expected_assets = {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in (root / "app/static").rglob("*")
        if path.is_file()
    }
    if (
        assets != expected_assets
        or not assets.get("app/static/index.html")
        or not all(
            any(
                name.startswith("app/static/assets/") and name.endswith(suffix) and content
                for name, content in assets.items()
            )
            for suffix in (".js", ".css")
        )
    ):
        raise ValueError("artifact dashboard assets are missing or differ from the build")


def verify_archives(root: Path, dist: Path, tag: str) -> None:
    release = parse_tag(tag)
    assert_project_versions(root, release.version)
    wheels, sdists = list(dist.glob("*.whl")), list(dist.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise ValueError("expected exactly one wheel and one sdist")
    if (
        wheels[0].name != f"codex_lb-{release.pypi_version}-py3-none-any.whl"
        or sdists[0].name != f"codex_lb-{release.pypi_version}.tar.gz"
    ):
        raise ValueError("archive filenames disagree with release version")
    with zipfile.ZipFile(wheels[0]) as archive:
        if len(archive.namelist()) != len(set(archive.namelist())):
            raise ValueError("duplicate wheel entries")
        contents = {name: archive.read(name) for name in archive.namelist() if not name.endswith("/")}
        metadata = [name for name in contents if name.endswith(".dist-info/METADATA")]
        if len(metadata) != 1:
            raise ValueError("expected one wheel metadata record")
        verify_contents(contents, metadata[0], root, release.pypi_version)
    with tarfile.open(sdists[0]) as archive:
        prefix = f"codex_lb-{release.pypi_version}/"
        contents = {}
        for member in archive.getmembers():
            if member.isdir():
                continue
            if not member.isfile() or not member.name.startswith(prefix):
                raise ValueError("unexpected sdist entry")
            name = member.name.removeprefix(prefix)
            if name in contents or ".." in Path(name).parts or Path(name).is_absolute():
                raise ValueError("duplicate or unsafe sdist entry")
            if any(
                part in {".git", ".kilo", ".agents", ".worktrees", ".venv", "node_modules", ".env"}
                or part.startswith(".env.")
                for part in Path(name).parts
            ):
                raise ValueError("local worktree or environment file in sdist")
            stream = archive.extractfile(member)
            assert stream is not None
            contents[name] = stream.read()
        verify_contents(contents, "PKG-INFO", root, release.pypi_version)
        for name in ("pyproject.toml", "frontend/package.json", "deploy/helm/codex-lb/Chart.yaml", "uv.lock"):
            if contents.get(name) != (root / name).read_bytes():
                raise ValueError(f"sdist release-managed file differs from checkout: {name}")
    print(f"verified wheel and sdist identity: {release.version}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--dist", type=Path, default=Path("dist"))
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()
    verify_archives(args.root.resolve(), args.dist.resolve(), args.tag)
    paths = sorted([*args.dist.glob("*.whl"), *args.dist.glob("*.tar.gz")])
    provenance = args.dist / "release-provenance.json"
    if provenance.is_file():
        paths.append(provenance)
    (args.dist / "SHA256SUMS").write_text(
        "".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in paths), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
