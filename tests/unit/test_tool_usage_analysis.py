from __future__ import annotations

import gzip
import json
import subprocess
import sys

import pytest

from scripts.analyze_tool_usage import analyze


@pytest.mark.parametrize("compressed", [False, True])
def test_tool_cli_deduplicates_session_replay_preserves_unknown_and_hides_payload(tmp_path, compressed):
    path = tmp_path / ("archive.jsonl.gz" if compressed else "archive.jsonl")
    call = {"type": "function_call", "call_id": "c1", "name": "search", "arguments": "SECRET_ARGUMENT"}
    records = [
        {"session_id": "session-a", "request_id": "r1", "payload": {"response": {"output": [call]}}},
        {
            "session_id": "session-a",
            "request_id": "r2",
            "payload": {
                "input": [
                    call,
                    {
                        "type": "function_call_output",
                        "call_id": "c1",
                        "output": '{"is_error":true,"content":"SECRET_RESULT"}',
                    },
                    {"type": "custom_tool_call", "call_id": "c2", "name": "shell", "input": "SECRET_SHELL"},
                    {
                        "type": "custom_tool_call_output",
                        "call_id": "c2",
                        "output": "text with error in it is not a proven error",
                    },
                ]
            },
        },
        {"session_id": "session-b", "payload": {"output": [call]}},
        {"session_id": "session-a", "payload": {"text": 'data: {"type":"computer_call","call_id":"c3"}\n\n'}},
        {
            "session_id": "session-a",
            "payload": {"input": [{"type": "computer_call_output", "call_id": "c3", "is_error": False}]},
        },
        {
            "request_id": "r3",
            "payload": {"type": {}, "output": [{"type": "function_call_output", "call_id": "orphan", "status": {}}]},
        },
    ]
    content = "\n".join(json.dumps(record) for record in records) + "\nmalformed SECRET_LINE\n"
    if compressed:
        with gzip.open(path, "wt", encoding="utf-8") as stream:
            stream.write(content)
    else:
        path.write_text(content, encoding="utf-8")
    process = subprocess.run(
        [sys.executable, "scripts/analyze_tool_usage.py", str(path)], capture_output=True, text=True
    )
    assert process.returncode == 0, process.stderr
    assert "SECRET" not in process.stdout + process.stderr
    body = json.loads(process.stdout)
    assert body["malformedLines"] == 1
    assert body["unmatchedResults"] == 1
    assert body["tools"] == [
        {
            "name": "computer",
            "calls": 1,
            "results": 1,
            "explicitErrors": 0,
            "explicitSuccesses": 1,
            "unknownOutcomes": 0,
        },
        {"name": "search", "calls": 2, "results": 1, "explicitErrors": 1, "explicitSuccesses": 0, "unknownOutcomes": 1},
        {"name": "shell", "calls": 1, "results": 1, "explicitErrors": 0, "explicitSuccesses": 0, "unknownOutcomes": 1},
    ]


def test_missing_archive_identity_does_not_collapse_unrelated_call_ids(tmp_path):
    path = tmp_path / "unknown.jsonl"
    record = {"payload": {"type": "function_call", "call_id": "repeat", "name": "f"}}
    path.write_text(json.dumps(record) + "\n" + json.dumps(record), encoding="utf-8")
    assert analyze([path])["tools"][0]["calls"] == 2


def test_tool_cli_io_failure_has_private_error(tmp_path):
    missing = tmp_path / "SECRET_PATH.jsonl"
    process = subprocess.run(
        [sys.executable, "scripts/analyze_tool_usage.py", str(missing)], capture_output=True, text=True
    )
    assert process.returncode == 2
    assert "SECRET_PATH" not in process.stderr
    assert "FileNotFoundError" in process.stderr


def test_explicit_single_session_correlates_across_request_ids(tmp_path):
    path = tmp_path / "scoped.jsonl"
    call = {"type": "function_call", "call_id": "c1", "name": "f"}
    records = [
        {"request_id": "r1", "payload": {"output": [call]}},
        {
            "request_id": "r2",
            "payload": {"input": [call, {"type": "function_call_output", "call_id": "c1", "is_error": True}]},
        },
    ]
    path.write_text("\n".join(json.dumps(record) for record in records), encoding="utf-8")
    assert analyze([path])["tools"][0]["calls"] == 2
    summary = analyze([path], single_session=True)
    assert summary["singleSession"] is True
    assert summary["tools"][0]["calls"] == 1
    assert summary["tools"][0]["explicitErrors"] == 1
