from __future__ import annotations

import json
import logging

import pytest

from app.core.runtime_logging import JsonFormatter, UtcDefaultFormatter, _redact_log_value

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("formatter", [JsonFormatter, UtcDefaultFormatter])
@pytest.mark.parametrize(
    "authorization",
    [
        'Authorization: Digest username="public", realm="api", response="SYNTHETIC_PRIVATE"',
        "Authorization: AWS4-HMAC-SHA256 Credential=public, SignedHeaders=host, Signature=SYNTHETIC_PRIVATE",
        '{"authorization": Digest username="public", malformed, response="SYNTHETIC_PRIVATE"}',
        "Proxy-Authorization: Bearer-x public, response=SYNTHETIC_PRIVATE",
        "Authorization: Bearer, response=SYNTHETIC_PRIVATE",
        'Authorization: Bearer "SYNTHETIC_PRIVATE", status=failed',
        "Authorization: Basic SYNTHETIC_PRIVATE, status=failed",
        "{'Proxy-Authorization': 'Basic SYNTHETIC_PRIVATE'}",
        "'Proxy-Authorization': AWS4-HMAC-SHA256 Credential=public, Signature=SYNTHETIC_PRIVATE",
        "'Proxy-Authorization': [REDACTED], Signature=SYNTHETIC_PRIVATE",
        "{'Proxy-Authorization': 'Basic [REDACTED] SYNTHETIC_PRIVATE'}",
    ],
)
def test_warning_formatters_hide_parameter_list_credentials_on_current_line(formatter, authorization):
    raw = authorization + "\nnext-line-status=503"
    record = logging.LogRecord("app.synthetic", logging.WARNING, __file__, 1, "%s", (raw,), None)
    rendered = formatter().format(record)
    message = json.loads(rendered)["message"] if formatter is JsonFormatter else rendered
    assert "SYNTHETIC_PRIVATE" not in message
    assert "[REDACTED]" in message
    assert "next-line-status=503" in message
    redacted = _redact_log_value(raw)
    assert _redact_log_value(redacted) == redacted
