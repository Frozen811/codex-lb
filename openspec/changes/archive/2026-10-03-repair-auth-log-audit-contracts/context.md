## Scope and rationale

Exactly UP-ISSUE-2028, UP-PR-2487 and UP-PR-2490. Authorization values may contain quoted commas, empty or malformed parameters and arbitrary whitespace. Credential parsing cannot safely decide which trailing fields are diagnostic context. An unquoted value is therefore masked through the current line end; a completely quoted field keeps its enclosing syntax.

Example: `authorization=Digest username="a,b", response="QA_SENTINEL", status=failed` becomes `authorization=[REDACTED]`. A following newline and `status=failed` survive. All credentials used in tests are inert fixtures.

TOTP and refresh production fixes are already present. Their independent validation covers HTTP rejection without enrollment/replay mutation and content-free refresh-attempt correlation on a real local OAuth error response. Cloud CI, public packages and live upstream behavior remain separate evidence scopes.
