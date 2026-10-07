"""Deterministic file-group sharding for integration-core and MySQL CI.

The integration-core slice is ``tests/integration`` minus the files owned by
the integration-bridge slice. To keep CI wallclock down the slice is split
into ``--shard-count`` shards. Recorded file durations take precedence; new
files use deterministic estimates accounting for parametrization, database
fixtures, migrations and explicit waits. Longest files go to the lightest shard.
All runners must use the same duration file for a given run.
The MySQL suite preserves its explicit file/node manifest and keeps all nodes
from one file on one runner; partial selections never expand to whole files.

Usage:
    python .github/scripts/pytest_shards.py --shard-count 6 --shard 1
        Print the file arguments for shard 1 (one per line).
    python .github/scripts/pytest_shards.py --shard-count 6 --verify
        Assert the shards form a complete, non-overlapping partition of the
        integration-core selection and that the bridge exclusions still exist.
    python .github/scripts/pytest_shards.py --suite mysql --shard-count 3 --shard-index 1
        Print the selected MySQL file/node arguments for shard 1.
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import sys
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
INTEGRATION_ROOT = Path("tests/integration")
MYSQL_MANIFEST = Path(".github/pytest-mysql-targets.txt")

# Files owned by the integration-bridge slice (see `make test-integration-bridge`).
# They are excluded here and must keep existing so neither slice silently loses them.
BRIDGE_FILES = (
    INTEGRATION_ROOT / "test_http_responses_bridge.py",
    INTEGRATION_ROOT / "test_proxy_websocket_responses.py",
)

# Default pytest collection globs (`python_files`); pyproject.toml does not override them.
TEST_FILE_GLOBS = ("test_*.py", "*_test.py")

DATABASE_FIXTURES = {"db_setup", "client", "async_client", "session", "app_instance", "_reset_db_state"}


def load_durations(path: Path | None) -> dict[str, float]:
    if path is None or not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Durations must be a JSON object mapping test files to seconds")
    for name, seconds in data.items():
        if not isinstance(name, str) or type(seconds) not in {int, float} or not math.isfinite(seconds) or seconds <= 0:
            raise ValueError("Every duration must have a file name and positive finite seconds")
    return data


def integration_core_files() -> list[Path]:
    root = REPO_ROOT / INTEGRATION_ROOT
    files: set[Path] = set()
    for pattern in TEST_FILE_GLOBS:
        files.update(path.relative_to(REPO_ROOT) for path in root.rglob(pattern))
    return sorted(files - set(BRIDGE_FILES))


def selector_function(tree: ast.Module, selector: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    body = tree.body
    parts = selector.split("::")[1:]
    for index, part in enumerate(parts):
        name = part.split("[", 1)[0]
        node = next(
            (
                item
                for item in body
                if isinstance(item, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef) and item.name == name
            ),
            None,
        )
        if (
            index == len(parts) - 1
            and isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
            and node.name.startswith("test_")
        ):
            return node
        if not isinstance(node, ast.ClassDef):
            break
        body = node.body
    raise ValueError(f"MySQL selector does not identify a test function: {selector}")


def mysql_file_groups() -> dict[Path, list[str]]:
    groups: dict[Path, list[str]] = {}
    seen: set[str] = set()
    for selector in (REPO_ROOT / MYSQL_MANIFEST).read_text(encoding="utf-8").split():
        if selector in seen:
            raise ValueError(f"Duplicate MySQL selector: {selector}")
        seen.add(selector)
        path = Path(selector.split("::", 1)[0])
        if path.is_absolute() or ".." in path.parts or path.suffix != ".py" or not (REPO_ROOT / path).is_file():
            raise ValueError(f"MySQL selector has an invalid test file: {selector}")
        if "::" in selector:
            selector_function(ast.parse((REPO_ROOT / path).read_text(encoding="utf-8")), selector)
        groups.setdefault(path, []).append(selector)
    for path, selectors in groups.items():
        if path.as_posix() in selectors and len(selectors) != 1:
            raise ValueError(f"Overlapping whole-file and node MySQL selectors: {path}")
        for index, selector in enumerate(selectors):
            for other in selectors[index + 1 :]:
                if other.startswith(selector + "[") or selector.startswith(other + "["):
                    raise ValueError(f"Overlapping parametrized MySQL selectors: {selector}, {other}")
    if not groups:
        raise ValueError("MySQL selection is empty")
    return groups


def file_weight(path: Path, durations: dict[str, float] | None = None) -> float:
    if durations and path.as_posix() in durations:
        return durations[path.as_posix()]
    return estimated_file_weight(path)


@lru_cache(maxsize=None)
def estimated_file_weight(path: Path) -> float:
    source = (REPO_ROOT / path).read_text(encoding="utf-8")
    weight = 0.5  # Include import/setup cost, even for a newly added empty file.
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) or not node.name.startswith("test_"):
            continue
        weight += function_weight(node)
    return weight


def function_weight(node: ast.FunctionDef | ast.AsyncFunctionDef, single_case: bool = False) -> float:
    cases = 1
    for decorator in node.decorator_list:
        if (
            not single_case
            and isinstance(decorator, ast.Call)
            and isinstance(decorator.func, ast.Attribute)
            and decorator.func.attr == "parametrize"
            and len(decorator.args) >= 2
            and isinstance(decorator.args[1], ast.List | ast.Tuple)
        ):
            cases *= max(1, len(decorator.args[1].elts))
    cost = 0.1
    if DATABASE_FIXTURES.intersection(argument.arg for argument in node.args.args):
        cost += 0.5
    for call in (item for item in ast.walk(node) if isinstance(item, ast.Call)):
        name = ast.unparse(call.func)
        if name.endswith(("run_upgrade", ".upgrade", ".downgrade", ".create_all", ".drop_all")):
            cost += 2.0
        if name.endswith(".sleep") and call.args and isinstance(call.args[0], ast.Constant):
            delay = call.args[0].value
            if isinstance(delay, int | float) and not isinstance(delay, bool) and delay > 0:
                cost += min(delay, 180)
    return cases * cost


def mysql_group_weight(path: Path, selectors: list[str], durations: dict[str, float] | None = None) -> float:
    if durations and path.as_posix() in durations:
        return durations[path.as_posix()]
    # MySQL rebuilds its schema once per file; partial files include only their
    # selected functions, rather than unrelated PostgreSQL migration tests.
    if selectors == [path.as_posix()]:
        return 2.0 + estimated_file_weight(path)
    tree = ast.parse((REPO_ROOT / path).read_text(encoding="utf-8"))
    return 2.5 + sum(function_weight(selector_function(tree, selector), "[" in selector) for selector in selectors)


def mysql_shard(
    groups: dict[Path, list[str]], shard: int, shard_count: int, durations: dict[str, float] | None = None
) -> list[str]:
    weights = {path.as_posix(): mysql_group_weight(path, selectors, durations) for path, selectors in groups.items()}
    files = shard_files(list(groups), shard, shard_count, weights)
    return [selector for path in files for selector in groups[path]]


def verify_mysql(groups: dict[Path, list[str]], shard_count: int, durations: dict[str, float] | None = None) -> None:
    expected = [selector for selectors in groups.values() for selector in selectors]
    seen: set[str] = set()
    file_owners: dict[str, int] = {}
    loads = []
    for shard in range(1, shard_count + 1):
        selected = mysql_shard(groups, shard, shard_count, durations)
        if not selected:
            raise SystemExit(f"MySQL shard {shard}/{shard_count} is empty")
        for selector in selected:
            if selector in seen:
                raise SystemExit(f"MySQL selector assigned more than once: {selector}")
            seen.add(selector)
            filename = selector.split("::", 1)[0]
            if file_owners.setdefault(filename, shard) != shard:
                raise SystemExit(f"MySQL file split across runners: {filename}")
        files = {Path(selector.split("::", 1)[0]) for selector in selected}
        loads.append(sum(mysql_group_weight(path, groups[path], durations) for path in files))
    if len(expected) != len(seen) or set(expected) != seen:
        raise SystemExit("MySQL shard partition has missing, duplicate or unexpected selectors")
    print(f"OK: {len(expected)} MySQL selectors in {len(groups)} files partitioned across {shard_count} shards")
    print("Estimated seconds per shard: " + ", ".join(f"{load:.1f}" for load in loads))


def shard_files(
    files: list[Path], shard: int, shard_count: int, durations: dict[str, float] | None = None
) -> list[Path]:
    # Greedy bin packing: heaviest file first onto the lightest shard.
    # Deterministic tie-breaks (file name, shard index) keep assignment stable.
    loads = [0.0] * shard_count
    shards: list[list[Path]] = [[] for _ in range(shard_count)]
    weights = {path: file_weight(path, durations) for path in files}
    for path in sorted(files, key=lambda p: (-weights[p], p)):
        target = min(range(shard_count), key=lambda i: (loads[i], i))
        loads[target] += weights[path]
        shards[target].append(path)
    return sorted(shards[shard - 1])


def verify(files: list[Path], shard_count: int, durations: dict[str, float] | None = None) -> None:
    for bridge_file in BRIDGE_FILES:
        if not (REPO_ROOT / bridge_file).is_file():
            raise SystemExit(
                f"bridge exclusion {bridge_file} does not exist; "
                "update BRIDGE_FILES and the Makefile integration slices together"
            )
    if not files:
        raise SystemExit("integration-core selection is empty")

    seen: dict[Path, int] = {}
    for shard in range(1, shard_count + 1):
        selected = shard_files(files, shard, shard_count, durations)
        if not selected:
            raise SystemExit(f"shard {shard}/{shard_count} selects no files")
        for path in selected:
            if path in seen:
                raise SystemExit(f"{path} assigned to both shard {seen[path]} and shard {shard}")
            seen[path] = shard

    missing = sorted(set(files) - set(seen))
    if missing:
        raise SystemExit("files not assigned to any shard: " + ", ".join(map(str, missing)))
    print(f"OK: {len(files)} integration-core test files partitioned across {shard_count} shards")
    loads = [
        sum(file_weight(path, durations) for path in shard_files(files, shard, shard_count, durations))
        for shard in range(1, shard_count + 1)
    ]
    print("Estimated seconds per shard: " + ", ".join(f"{load:.1f}" for load in loads))


def update_durations(reports: list[Path], destination: Path, suite: str = "integration-core") -> None:
    """Refresh history from pytest JUnit reports (setup + call + teardown time)."""
    measured: dict[str, float] = {}
    mysql_files = {path.as_posix() for path in mysql_file_groups()} if suite == "mysql" else None
    for report in reports:
        for case in ET.parse(report).iter("testcase"):
            if case.find("skipped") is not None:
                continue
            filename = case.get("file")
            if not filename:
                parts = case.get("classname", "").split(".")
                while parts:
                    candidate = Path(*parts).with_suffix(".py")
                    if (REPO_ROOT / candidate).is_file():
                        filename = candidate.as_posix()
                        break
                    parts.pop()
            if filename and (
                filename in mysql_files if mysql_files is not None else filename.startswith("tests/integration/")
            ):
                seconds = float(case.get("time", "0"))
                if math.isfinite(seconds) and seconds > 0:
                    measured[filename] = measured.get(filename, 0) + seconds
    if not measured:
        raise ValueError(f"JUnit reports contain no {suite} test durations")
    history = load_durations(destination)
    history.update(measured)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(dict(sorted(history.items())), indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", choices=("integration-core", "mysql"), default="integration-core")
    parser.add_argument("--shard-count", type=int, help="total shards (default: core 6, MySQL 3)")
    parser.add_argument("--durations-file", type=Path, help="JSON file with recorded file durations in seconds")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--shard", "--shard-index", dest="shard", type=int, help="1-based shard index to print selectors for"
    )
    group.add_argument("--verify", action="store_true", help="assert shards partition the full selection")
    group.add_argument("--update-from-junit", type=Path, nargs="+", help="refresh duration history from pytest reports")
    args = parser.parse_args()
    args.shard_count = args.shard_count if args.shard_count is not None else (3 if args.suite == "mysql" else 6)

    if args.update_from_junit:
        if args.durations_file is None:
            parser.error("--update-from-junit requires --durations-file")
        update_durations(args.update_from_junit, args.durations_file, args.suite)
        return

    if args.shard_count < 1:
        parser.error("--shard-count must be >= 1")
    if args.shard is not None and not 1 <= args.shard <= args.shard_count:
        parser.error("--shard must be between 1 and --shard-count")

    durations = load_durations(args.durations_file)
    if args.suite == "mysql":
        groups = mysql_file_groups()
        if args.verify:
            verify_mysql(groups, args.shard_count, durations)
        else:
            sys.stdout.write("\n".join(mysql_shard(groups, args.shard, args.shard_count, durations)) + "\n")
        return
    files = integration_core_files()
    if args.verify:
        verify(files, args.shard_count, durations)
        return
    sys.stdout.write(
        "\n".join(str(path) for path in shard_files(files, args.shard, args.shard_count, durations)) + "\n"
    )


if __name__ == "__main__":
    main()
