# OAuth callback lifecycle and privacy context

Requirements are in [spec.md](spec.md). The callback listener is a temporary
account-login service, separate from the dashboard HTTP server.

## Failed listener startup

Purpose: make occupied ports and cancellation observable without leaking login
credentials or retaining an initialized runner. Listener startup owns cleanup
before propagating failure/cancellation. Browser flow state remains pending
when bind fails so a remote/manual callback can still complete the flow; it is
not changed into an automatic successful login or a forced device-code flow.

The diagnostic contains bind host, port and exception type only. It omits
state, PKCE verifier, authorization URL and raw error text. Callback access
logging remains suppressed. For example, another login already owns port 1455:
startup releases its failed runner, records a safe warning and the operator
pastes the resulting browser callback into the dashboard's existing input.
Device-code login is a separate dialog choice. Token exchange must still pass
state/identity and persisted-flow checks.

## Verification scope

The SETUP-06 regressions use a real occupied TCP port, cancellation after
initialization and the actual start/status/manual-callback routes. Token
exchange is explicitly synthetic; account persistence/status success does not
certify an OpenAI login. Existing OAuth expiry, race, replay and callback-log
tests remain in the focused suite. A successful readiness response is not
evidence that this callback listener is bound. See docs/getting-started.md and
issues-check.md section 25 for operator guidance and rehearsal limits.
