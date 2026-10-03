from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

from app.core.runtime_logging import (
    FileLogFormatter,
    JsonFormatter,
    UtcDefaultFormatter,
    _error_log_field,
    redact_rendered_log_text,
)

pytestmark = pytest.mark.unit

AUTHORIZATION_PROBES = [
    'authorization=Digest username="a,b", response="QA_SENTINEL"',
    'authorization=Digest username="public",,response="QA_SENTINEL"',
    "authorization=Digest username=u, malformed, response=QA_SENTINEL",
    "authorization='Digest username=x, response=QA_SENTINEL', status=failed",
    "headers={'authorization': 'Basic QA_SENTINEL'}",
    '{"authorization": Basic QA_SENTINEL, retrying upstream request}',
    '{"authorization": Digest username="public", malformed, response="QA_SENTINEL"}',
    "authorization=Bearer abc QA_SENTINEL, status=ok",
    "authorization=Bearer [REDACTED] QA_SENTINEL",
    "authorization=Digest username=a, status=QA_SENTINEL",
    "authorization=Digest username=a&response=QA_SENTINEL",
]


@pytest.mark.parametrize("probe", AUTHORIZATION_PROBES)
@pytest.mark.parametrize("surface", ["field", "text", "json", "exception-text", "exception-json"])
def test_authorization_credentials_do_not_reach_operator_output(probe: str, surface: str) -> None:
    if surface == "field":
        rendered = _error_log_field(probe)
    else:
        exc_info = None
        if surface.startswith("exception"):
            exc_info = (RuntimeError, RuntimeError(probe), None)
        record = logging.LogRecord("app.audit", logging.WARNING, __file__, 1, probe, (), exc_info)
        formatter = JsonFormatter() if surface.endswith("json") else UtcDefaultFormatter(use_colors=False)
        rendered = formatter.format(record)
        if surface.endswith("json"):
            assert json.loads(rendered)["level"] == "WARNING"
    assert "QA_SENTINEL" not in rendered
    assert "[REDACTED]" in rendered


@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
@pytest.mark.parametrize("probe", AUTHORIZATION_PROBES)
def test_authorization_redaction_is_idempotent_and_preserves_following_lines(probe: str, newline: str) -> None:
    value = probe + newline + "safe diagnostic line"
    rendered = redact_rendered_log_text(value)
    assert "QA_SENTINEL" not in rendered
    assert rendered.endswith(newline + "safe diagnostic line")
    assert redact_rendered_log_text(rendered) == rendered


@pytest.mark.parametrize("log_format", ["text", "json"])
def test_authorization_credentials_do_not_reach_actual_log_file(tmp_path: Path, log_format: str) -> None:
    path = tmp_path / "operator.log"
    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setFormatter(FileLogFormatter(log_format))
    logger = logging.Logger("app.authorization-audit", level=logging.WARNING)
    logger.addHandler(handler)
    try:
        for probe in AUTHORIZATION_PROBES:
            logger.warning("upstream rejected %s", probe, extra={"status": "failed"})
        handler.flush()
    finally:
        logger.removeHandler(handler)
        handler.close()
    output = path.read_text(encoding="utf-8")
    assert "QA_SENTINEL" not in output
    assert len(output.splitlines()) == len(AUTHORIZATION_PROBES)
    if log_format == "json":
        assert all(json.loads(line)["status"] == "failed" for line in output.splitlines())


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("authorization='Digest response=QA_SENTINEL', status=failed", "authorization='[REDACTED]', status=failed"),
        (
            '{"authorization": "Bearer QA_SENTINEL", "status": "failed"}',
            '{"authorization": "[REDACTED]", "status": "failed"}',
        ),
        (
            "{'authorization': b'QA_SENTINEL', 'status': 'failed'}",
            "{'authorization': b'[REDACTED]', 'status': 'failed'}",
        ),
        ('authorization="QA_SENTINEL', "authorization=[REDACTED]"),
    ],
)
def test_complete_quoted_authorization_keeps_context_and_unterminated_value_is_masked(raw: str, expected: str) -> None:
    assert redact_rendered_log_text(raw) == expected
    assert redact_rendered_log_text(expected) == expected
