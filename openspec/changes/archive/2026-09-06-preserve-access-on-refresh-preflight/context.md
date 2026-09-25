# Context

## Preflight Refresh and Access Token Lifetime

When requests are dispatched through the load balancer, accounts whose `last_refresh` timestamp is older than the configured refresh interval undergo preflight refresh to ensure their tokens remain fresh.
If upstream rejects the refresh token (e.g. because of revocation, session termination, or invalid grant), the background exchange fails permanently.

In cases where the account's existing OAuth `access_token` JWT has not yet expired (e.g., remaining TTL of minutes or hours), immediately aborting the request or raising an error wastes the remainder of the session.
By allowing `ensure_fresh` to gracefully retain the unexpired access token while marking the account as `reauth_required`, existing sessions and immediate proxy calls succeed until token expiry, providing seamless continuity.
