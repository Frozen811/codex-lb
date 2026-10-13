"""Pure identity, lifecycle and echo checks for complete HTTP bridge transcripts."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from typing import cast

from app.core.types import JsonValue
from app.core.utils.sse import parse_sse_data_json

_TOOL_CALL_TYPES = frozenset({"function_call", "custom_tool_call", "apply_patch_call"})
_TOOL_OUTPUT_TYPES = frozenset({"function_call_output", "custom_tool_call_output", "apply_patch_call_output"})
_TOOL_ITEM_TYPES = _TOOL_CALL_TYPES | _TOOL_OUTPUT_TYPES


def output_item_identity(item: Mapping[str, JsonValue]) -> dict[str, str]:
    """Return the stable identity fields present on an output item.

    ``id`` identifies the provider-owned output item, while ``call_id`` pairs
    tool calls with their outputs.  ``type`` is included as the discriminator;
    values with another shape are intentionally ignored so callers can fail
    closed through :func:`output_item_identity_is_valid`.
    """

    identity: dict[str, str] = {}
    for field in ("id", "call_id", "type"):
        value = item.get(field)
        if isinstance(value, str) and value:
            identity[field] = value
    return identity


def output_item_identity_is_valid(identity: Mapping[str, str]) -> bool:
    """Validate the identity required for a Responses output-item lifecycle."""

    item_type = identity.get("type")
    if not isinstance(item_type, str) or not item_type:
        return False
    if item_type in _TOOL_CALL_TYPES:
        return bool(identity.get("id")) and bool(identity.get("call_id"))
    if item_type in _TOOL_OUTPUT_TYPES:
        return bool(identity.get("call_id"))
    # A persisted non-tool output is replayable only when it can be matched to
    # the same provider item on a subsequent echo.  ``compaction`` is the one
    # intentional identity-less envelope: it represents a boundary marker,
    # not a repeatable output item.
    if item_type == "compaction":
        return True
    return bool(identity.get("id"))


def output_item_identities_match(expected: Mapping[str, str], actual: Mapping[str, str]) -> bool:
    """Require every identity field observed in ``expected`` on ``actual``."""

    return all(actual.get(field) == value for field, value in expected.items())


def _without_response_owned_id(item: JsonValue) -> JsonValue:
    if not isinstance(item, dict):
        return item
    copied = dict(item)
    copied.pop("id", None)
    return copied


def _canonical_item(item: JsonValue, *, omit_status: bool = False) -> str:
    normalized = _without_response_owned_id(item)
    if isinstance(normalized, dict):
        normalized = dict(normalized)
        if omit_status:
            normalized.pop("status", None)
    return json.dumps(normalized, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def items_match_for_echo(left: JsonValue, right: JsonValue) -> bool:
    """Compare two echoed items while allowing an omitted status or provider id.

    Providers may omit the optional ``status`` when echoing a completed item,
    but two explicit and different statuses describe divergent execution
    state and must not be treated as the same item.
    """

    if isinstance(left, dict) and isinstance(right, dict):
        left_status = left.get("status")
        right_status = right.get("status")
        if "status" in left and "status" in right and left_status != right_status:
            return False
    return _canonical_item(left, omit_status=True) == _canonical_item(right, omit_status=True)


def materialize_terminal_output(
    events: object,
    *,
    expected_response_id: str | None = None,
    expected_terminal_type: str | None = None,
) -> list[JsonValue] | None:
    """Read a terminal answer only after validating observed item lifecycles."""
    if not isinstance(events, Sequence) or isinstance(events, (str, bytes, bytearray)):
        return None
    added: dict[int, dict[str, str]] = {}
    done: dict[int, dict[str, JsonValue]] = {}
    unindexed_done: list[JsonValue] = []
    attempt_response_id: str | None = None
    for event_text in events:
        if not isinstance(event_text, str):
            return None
        payload = parse_sse_data_json(event_text)
        if payload is None:
            continue
        event_type = payload.get("type")
        if not isinstance(event_type, str):
            return None
        if event_type in {"response.created", "response.failed", "error"}:
            added.clear()
            done.clear()
            unindexed_done.clear()
            response = payload.get("response")
            identifier = response.get("id") if isinstance(response, dict) else None
            attempt_response_id = identifier if isinstance(identifier, str) else None
            continue
        if event_type in {"response.output_item.added", "response.output_item.done"}:
            item = payload.get("item")
            if not isinstance(item, dict):
                return None
            index = payload.get("output_index")
            if index is None and event_type == "response.output_item.done" and not added:
                unindexed_done.append(item)
                continue
            if type(index) is not int or index < 0:
                return None
            identity = output_item_identity(item)
            if not output_item_identity_is_valid(identity):
                return None
            if event_type == "response.output_item.added":
                if index in added or index in done:
                    return None
                added[index] = identity
            else:
                if index in added and not output_item_identities_match(added[index], identity):
                    return None
                previous = done.get(index)
                if previous is not None and previous != item:
                    return None
                done[index] = item
            continue
        if event_type not in {"response.completed", "response.incomplete"}:
            continue
        response = payload.get("response")
        if not isinstance(response, dict) or added.keys() - done.keys():
            return None
        response_id = response.get("id")
        if (
            not isinstance(response_id, str)
            or not response_id.strip()
            or (expected_response_id is not None and response_id != expected_response_id)
            or (attempt_response_id is not None and response_id != attempt_response_id)
            or (expected_terminal_type is not None and event_type != expected_terminal_type)
        ):
            return None
        if "output" not in response:
            return [done[index] for index in sorted(done)] + unindexed_done
        output = response["output"]
        if not isinstance(output, list) or any(not isinstance(item, dict) for item in output):
            return None
        for index, completed in done.items():
            if index >= len(output):
                return None
            terminal_item = output[index]
            if (
                not isinstance(terminal_item, dict)
                or not output_item_identities_match(
                    output_item_identity(completed), output_item_identity(terminal_item)
                )
                or not items_match_for_echo(completed, terminal_item)
            ):
                return None
        return output
    return None


def deduplicate_exact_replayed_tool_items(items: Iterable[JsonValue]) -> list[JsonValue] | None:
    """Remove exact repeated tool call/output echoes without masking conflicts.

    A replay request can echo a tool item already retained in the durable
    transcript.  Repeated items with the same ``call_id`` are dropped only
    when their canonical content agrees exactly.  A second item with the same
    call id but different type or content is ambiguous and returns ``None`` so
    a caller can fail closed.  Non-tool items and malformed tool entries are
    preserved for the caller's normal validation.
    """

    materialized = list(items)
    seen_calls: dict[str, tuple[str, str]] = {}
    seen_outputs: dict[str, tuple[str, str]] = {}
    drop: set[int] = set()

    for index, item in enumerate(materialized):
        if not isinstance(item, dict):
            continue
        item_type = item.get("type")
        if not isinstance(item_type, str):
            # Preserve malformed entries for the caller's normal validation;
            # checking membership on an array/object would raise TypeError.
            continue
        if item_type not in _TOOL_ITEM_TYPES:
            continue
        call_id = item.get("call_id")
        if not isinstance(call_id, str) or not call_id:
            continue

        canonical = _canonical_item(cast(JsonValue, item))
        seen = seen_calls if item_type in _TOOL_CALL_TYPES else seen_outputs
        previous = seen.get(call_id)
        if previous is None:
            seen[call_id] = (item_type, canonical)
            continue
        previous_type, previous_canonical = previous
        if previous_type != item_type or previous_canonical != canonical:
            return None
        drop.add(index)

    return [item for index, item in enumerate(materialized) if index not in drop]


# Keep the underscore spellings used by the forthcoming capture/recovery work
# available to focused tests without making the helpers part of any runtime
# wiring in this release.
_output_item_identity = output_item_identity
_output_item_identity_is_valid = output_item_identity_is_valid
_output_item_identities_match = output_item_identities_match
_items_match_for_echo = items_match_for_echo
_deduplicate_exact_replayed_tool_items = deduplicate_exact_replayed_tool_items
