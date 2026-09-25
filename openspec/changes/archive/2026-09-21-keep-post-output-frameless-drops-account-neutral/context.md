# Context: Post-Output Frame-Less Drops Account-Neutrality

## Background & Rationale

When an upstream WebSocket connection drops abruptly without an RFC 6455 close frame
(represented as `close_code is None` or adapter-synthesized `1006`), it reflects
a transport-level failure such as an OS network reset, intermediate proxy drop,
or connection loss.

Issue #1754 recognized that charging an account for a frame-less drop before
any application-layer response event occurred was incorrect, because the account
never spoke. However, it restricted account-neutrality to `response_events_seen == 0`
and `not upstream_output_observed`.

In production (Issue #2074), long streaming responses can experience occasional
transport disconnects. Because `response_events_seen > 0`, the previous code
treated the transport drop as an account failure, incrementing `error_count`
and triggering error backoff on the account.

This inverted the evidence:
1. Valid response events and generated tokens are proof that the account's credentials,
   entitlements, and upstream model pipeline were operational.
2. A missing close frame indicates that upstream never authored a close frame
   (unlike 1008 policy violation or 1011 upstream error).
3. The drop is therefore transport noise, not an account fault.

## Decisions

- `_is_account_neutral_transport_drop`: returns `True` for `close_code in (None, 1006)`.
- `account_neutral_transport_drop` in `upstream_events.py`:
  Evaluates to `True` for `close_code in (None, 1006)` without requiring `not upstream_output_observed`.
- `penalize_account`: remains `False` when `account_neutral_transport_drop` is `True`.
- `_record_http_bridge_account_timeout_signal`: only receives eventless drops
  (`observed_response_events == 0 and not upstream_output_observed`), so post-output
  transport drops do not trigger drain backoff.
- Replay safety is unaffected: `_http_bridge_request_state_holds_safe_replay` and
  `response_events_seen > 0` ensure that partially streamed requests are never
  improperly replayed across accounts.
