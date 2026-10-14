"""Summarize explicit tool observations from local conversation archives."""

from __future__ import annotations

import argparse
import gzip
import json
import zlib
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CALL_TYPES = {"function_call", "custom_tool_call", "computer_call"}
RESULT_TYPES = {"function_call_output", "custom_tool_call_output", "computer_call_output"}


@dataclass
class ToolObservation:
    name: str


def _items(payload: Any, depth: int = 0) -> Iterator[dict[str, Any]]:
    if depth > 12:
        return
    if isinstance(payload, str):
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            parsed = None
        if parsed is not None:
            yield from _items(parsed, depth + 1)
            return
        # Archive SSE records can contain several framed events.
        for line in payload.splitlines():
            if line.startswith("data:"):
                try:
                    yield from _items(json.loads(line[5:].strip()), depth + 1)
                except json.JSONDecodeError:
                    continue
        return
    if isinstance(payload, list):
        for item in payload:
            yield from _items(item, depth + 1)
    elif isinstance(payload, dict):
        item_type = payload.get("type")
        if isinstance(item_type, str) and item_type in CALL_TYPES | RESULT_TYPES:
            yield payload
            return
        # Visit only protocol containers, never arguments, result contents or headers.
        for key in ("input", "output", "response", "item", "payload", "text"):
            if key in payload:
                yield from _items(payload[key], depth + 1)


def _outcome(item: dict[str, Any]) -> tuple[bool, bool]:
    output = item.get("output")
    if isinstance(output, str):
        try:
            output = json.loads(output)
        except json.JSONDecodeError:
            output = None
    values = [item, output] if isinstance(output, dict) else [item]
    error = any(
        value.get("is_error") is True
        or value.get("status") in ("error", "failed")
        or isinstance(value.get("error"), dict)
        for value in values
    )
    success = any(value.get("is_error") is False or value.get("status") in ("success", "succeeded") for value in values)
    return error, success and not error


def analyze(paths: Iterable[Path], *, single_session: bool = False) -> dict[str, Any]:
    observations: dict[tuple[str, str], ToolObservation] = {}
    results: dict[tuple[str, str], tuple[bool, bool]] = {}
    malformed = 0
    records = 0
    request_scoped = 0
    for path in paths:
        opener = gzip.open if path.name.endswith(".gz") else open
        with opener(path, "rt", encoding="utf-8") as stream:
            for line in stream:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    malformed += 1
                    continue
                if not isinstance(record, dict):
                    malformed += 1
                    continue
                records += 1
                extra = record.get("extra") if isinstance(record.get("extra"), dict) else {}
                scope = record.get("session_id") or extra.get("session_id") or record.get("conversation_id")
                if not isinstance(scope, str):
                    scope = record.get("request_id")
                    request_scoped += 1
                if not isinstance(scope, str) or not scope:
                    # Never collapse unrelated calls when identifying metadata is missing.
                    scope = f"record:{records}"
                if single_session:
                    scope = "explicit-single-session"
                for item in _items(record.get("payload")):
                    call_id = item.get("call_id") or item.get("id")
                    if not isinstance(call_id, str) or not call_id:
                        continue
                    key = (scope, call_id)
                    if item["type"] in CALL_TYPES:
                        name = item.get("name") if item["type"] != "computer_call" else "computer"
                        if isinstance(name, str) and name:
                            observations.setdefault(key, ToolObservation(name=name))
                    else:
                        error, success = _outcome(item)
                        previous = results.get(key, (False, False))
                        results[key] = (error or previous[0], success or previous[1])
    summaries: dict[str, dict[str, Any]] = {}
    for key, observation in observations.items():
        outcome = results.get(key)
        row = summaries.setdefault(
            observation.name,
            {
                "name": observation.name,
                "calls": 0,
                "results": 0,
                "explicitErrors": 0,
                "explicitSuccesses": 0,
                "unknownOutcomes": 0,
            },
        )
        row["calls"] += 1
        if outcome is not None:
            row["results"] += 1
        if outcome is not None and outcome[0]:
            row["explicitErrors"] += 1
        elif outcome is not None and outcome[1]:
            row["explicitSuccesses"] += 1
        else:
            row["unknownOutcomes"] += 1
    return {
        "records": records,
        "malformedLines": malformed,
        "requestScopedRecords": request_scoped,
        "singleSession": single_session,
        "unmatchedResults": len(results.keys() - observations.keys()),
        "tools": [summaries[name] for name in sorted(summaries)],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", type=Path, nargs="+", help="Explicit JSONL or gzip archive files")
    parser.add_argument(
        "--single-session",
        action="store_true",
        help="Input files contain only one session; correlate across request IDs",
    )
    args = parser.parse_args()
    try:
        summary = analyze(args.archives, single_session=args.single_session)
    except (OSError, UnicodeError, EOFError, zlib.error) as exc:
        parser.exit(2, f"Archive analysis failed: {type(exc).__name__}\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
