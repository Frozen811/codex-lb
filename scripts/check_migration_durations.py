#!/usr/bin/env python3
"""Stdlib-only raw SQL safety gate; actual timings live in benchmark_migrations."""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

HIGH_VOLUME_TABLES = frozenset({"request_logs", "usage_history", "additional_usage_history"})
RATCHET_CUTOFF_DATE = "20260723_000000"
_IDENTIFIER = r'(?:[a-z_][a-z_0-9]*|"[^"]+"|`[^`]+`|\[[^\]]+\])'
_UPDATE = re.compile(rf"\bUPDATE\s+(?:ONLY\s+)?({_IDENTIFIER}(?:\s*\.\s*{_IDENTIFIER})?)\s", re.I)
_SQL_NOISE = re.compile(r"'(?:''|[^'])*'|--[^\n]*|/\*.*?\*/", re.S)
_LOWER_BOUND = re.compile(r"\bID\s*>=\s*:START_ID\b", re.I)
_UPPER_BOUND = re.compile(r"\bID\s*<\s*:END_ID\b", re.I)


def _sql_values(node: ast.AST, assignments: dict[str, list[ast.AST]], seen: frozenset[str] = frozenset()) -> set[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return {node.value}
    if isinstance(node, ast.Name) and node.id in assignments and node.id not in seen:
        return {sql for value in assignments[node.id] for sql in _sql_values(value, assignments, seen | {node.id})}
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return {
            left + right
            for left in _sql_values(node.left, assignments, seen)
            for right in _sql_values(node.right, assignments, seen)
        }
    if isinstance(node, ast.JoinedStr):
        candidates = {""}
        for part in node.values:
            if isinstance(part, ast.FormattedValue):
                if part.conversion != -1 or part.format_spec is not None:
                    return set()
                part = part.value
            candidates = {prefix + value for prefix in candidates for value in _sql_values(part, assignments, seen)}
        return candidates
    if isinstance(node, ast.Call) and node.args:
        name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
        if name == "text":
            return _sql_values(node.args[0], assignments, seen)
    return set()


def analyze_migration_file(path: Path) -> list[str]:
    """Reject supported raw SQL UPDATE forms without explicit bound parameters."""
    if path.stem < RATCHET_CUTOFF_DATE:
        return []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeError) as exc:
        return [f"Failed to parse {path.name}: {type(exc).__name__}"]
    # Keep all possible values conservatively; a later assignment must not hide
    # an earlier unsafe execution. Annotated and ordinary assignments both count.
    assignments: dict[str, list[ast.AST]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assignments.setdefault(target.id, []).append(node.value)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            assignments.setdefault(node.target.id, []).append(node.value)
    violations: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
        if name not in {"execute", "text", "execute_batched_backfill"}:
            continue
        for sql in {value for arg in node.args for value in _sql_values(arg, assignments)}:
            clean = _SQL_NOISE.sub(" ", sql)
            for update in _UPDATE.finditer(clean):
                table = re.split(r"\s*\.\s*", update[1])[-1].strip('"`[]').lower()
                if table not in HIGH_VOLUME_TABLES:
                    continue
                statement = clean[update.end() :].split(";", 1)[0]
                where = re.split(r"\bWHERE\b", statement, maxsplit=1, flags=re.I)
                bounded = (
                    len(where) == 2
                    and not re.search(r"\b(?:OR|NOT|SELECT)\b", where[1], re.I)
                    and _LOWER_BOUND.search(where[1]) is not None
                    and _UPPER_BOUND.search(where[1]) is not None
                )
                if not bounded:
                    violations.add(f"{path.name}: Unbatched UPDATE on high-volume table '{table}'")
    return sorted(violations)


def check_all_migrations(versions_dir: Path) -> list[str]:
    if not versions_dir.is_dir():
        return [f"Versions directory not found: {versions_dir}"]
    return [error for path in sorted(versions_dir.glob("*.py")) for error in analyze_migration_file(path)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--versions-dir", type=Path, default=Path("app/db/alembic/versions"))
    parser.add_argument("--benchmark", action="store_true", help="Use python -m scripts.benchmark_migrations instead")
    args = parser.parse_args()
    if args.benchmark:
        parser.error("Use python -m scripts.benchmark_migrations with an explicit baseline for a database benchmark")
    violations = check_all_migrations(args.versions_dir)
    for violation in violations:
        print(f"VIOLATION: {violation}", file=sys.stderr)
    if not violations:
        print("All static migration safety checks passed; runtime duration is not measured.")
    raise SystemExit(bool(violations))


if __name__ == "__main__":
    main()
