# Why

Closed issue #1754 made an abrupt, frame-less HTTP bridge transport drop
account-neutral only when `response_events_seen == 0` and no output had been
observed. However, a transport drop with no upstream-authored close frame
(`None` or adapter-synthesized RFC 6455 `1006`) is transport evidence, not
account ill-health. The fact that response events or model output were already
emitted is positive evidence that upstream authentication, model admission,
and application processing succeeded.

Penalizing account health for mid-stream or post-output transport drops
unnecessarily degrades healthy accounts due to normal network churn or socket
drops. Application progress must govern replay safety (the request must still
fail closed when replay is unsafe), not account-health attribution.

# What Changes

- Update `_is_account_neutral_transport_drop` to classify all frame-less
  websocket closures (`close_code in (None, 1006)`) as account-neutral,
  regardless of whether response events or buffered model output were observed.
- In the HTTP bridge reader failure path, keep frame-less transport drops
  account-neutral (`penalize_account=False`) even when `upstream_output_observed`
  is True or `response_events_seen > 0`.
- Maintain the windowed eventless account failure signal strictly for
  eventless drops: drops where `observed_response_events == 0 and not upstream_output_observed`
  feed `_record_http_bridge_account_timeout_signal`, whereas drops after output
  has started do not.
- Replay safety remains strict: an interrupted request with observed output
  or response events cannot be replayed and fails closed to the client.

# Capabilities

## Modified Capabilities

- `responses-api-compat`: HTTP bridge abrupt frame-less upstream drops remain
  account-neutral regardless of whether response events or model output were
  observed, while eventless drops continue to feed the windowed drain signal.

# Impact

Accounts are no longer penalized with error backoff when a socket drops
mid-stream after successfully authenticating and producing output. Replay
invariants and fail-closed behaviors remain preserved.
