from __future__ import annotations

import pytest

from app.core.openai.requests import ResponsesCompactRequest, ResponsesRequest
from app.db.models import StickySessionKind
from app.modules.proxy._service.compact import _sticky_key_for_compact_request
from app.modules.proxy.affinity import (
    SUBAGENT_PROMPT_CACHE_MAX_AGE_SECONDS,
    _effective_prompt_cache_max_age_seconds,
    _is_subagent_headers,
    _sticky_key_for_responses_request,
)

pytestmark = pytest.mark.unit


def test_is_subagent_headers_detection() -> None:
    assert _is_subagent_headers({}) is False
    assert _is_subagent_headers({"authorization": "Bearer foo"}) is False

    # x-parent-session-id
    assert _is_subagent_headers({"x-parent-session-id": "parent-123"}) is True
    assert _is_subagent_headers({"x-parent-session-id": "  "}) is False

    # x-openai-subagent
    assert _is_subagent_headers({"x-openai-subagent": "true"}) is True
    assert _is_subagent_headers({"x-openai-subagent": "1"}) is True
    assert _is_subagent_headers({"x-openai-subagent": "subagent-name"}) is True
    assert _is_subagent_headers({"x-openai-subagent": "false"}) is False
    assert _is_subagent_headers({"x-openai-subagent": "0"}) is False
    assert _is_subagent_headers({"x-openai-subagent": "no"}) is False

    # x-codex-parent-thread-id
    assert _is_subagent_headers({"x-codex-parent-thread-id": "thread-abc"}) is True
    assert _is_subagent_headers({"x-codex-parent-thread-id": ""}) is False


def test_effective_prompt_cache_max_age_seconds() -> None:
    # Non-subagent uses configured TTL
    assert _effective_prompt_cache_max_age_seconds({}, 3600) == 3600
    assert _effective_prompt_cache_max_age_seconds({}, 120) == 120

    # Subagent caps at 300s
    assert _effective_prompt_cache_max_age_seconds({"x-parent-session-id": "p1"}, 3600) == 300
    assert _effective_prompt_cache_max_age_seconds({"x-openai-subagent": "true"}, 3600) == 300
    assert _effective_prompt_cache_max_age_seconds({"x-codex-parent-thread-id": "t1"}, 3600) == 300

    # If configured TTL is even shorter than 300s, subagent respects the shorter one
    assert _effective_prompt_cache_max_age_seconds({"x-parent-session-id": "p1"}, 120) == 120


def test_sticky_key_for_responses_request_subagent_ttl() -> None:
    req = ResponsesRequest(
        model="gpt-5",
        prompt_cache_key="my-key",
        input=[{"type": "message", "role": "user", "content": "hi"}],
        instructions="test",
    )

    # Regular request
    policy = _sticky_key_for_responses_request(
        req,
        headers={},
        codex_session_affinity=False,
        openai_cache_affinity=True,
        openai_cache_affinity_max_age_seconds=3600,
        sticky_threads_enabled=False,
    )
    assert policy.kind == StickySessionKind.PROMPT_CACHE
    assert policy.max_age_seconds == 3600

    # Subagent with x-parent-session-id
    policy_subagent = _sticky_key_for_responses_request(
        req,
        headers={"x-parent-session-id": "sess-parent-456"},
        codex_session_affinity=False,
        openai_cache_affinity=True,
        openai_cache_affinity_max_age_seconds=3600,
        sticky_threads_enabled=False,
    )
    assert policy_subagent.kind == StickySessionKind.PROMPT_CACHE
    assert policy_subagent.max_age_seconds == SUBAGENT_PROMPT_CACHE_MAX_AGE_SECONDS

    # Thread affinity with subagent
    policy_thread_subagent = _sticky_key_for_responses_request(
        req,
        headers={"x-parent-session-id": "sess-parent-456", "thread-id": "child-thread"},
        codex_session_affinity=True,
        openai_cache_affinity=True,
        openai_cache_affinity_max_age_seconds=3600,
        sticky_threads_enabled=False,
    )
    assert policy_thread_subagent.kind == StickySessionKind.PROMPT_CACHE
    assert policy_thread_subagent.max_age_seconds == SUBAGENT_PROMPT_CACHE_MAX_AGE_SECONDS


def test_sticky_key_for_compact_request_subagent_ttl() -> None:
    req = ResponsesCompactRequest(
        model="gpt-5",
        input=[{"type": "message", "role": "user", "content": "hi"}],
        instructions="test",
    )

    # Regular request
    policy = _sticky_key_for_compact_request(
        req,
        headers={},
        codex_session_affinity=False,
        openai_cache_affinity=True,
        openai_cache_affinity_max_age_seconds=3600,
        sticky_threads_enabled=False,
    )
    assert policy.kind == StickySessionKind.PROMPT_CACHE
    assert policy.max_age_seconds == 3600

    # Subagent
    policy_subagent = _sticky_key_for_compact_request(
        req,
        headers={"x-parent-session-id": "parent-1"},
        codex_session_affinity=False,
        openai_cache_affinity=True,
        openai_cache_affinity_max_age_seconds=3600,
        sticky_threads_enabled=False,
    )
    assert policy_subagent.kind == StickySessionKind.PROMPT_CACHE
    assert policy_subagent.max_age_seconds == 300
