# Account identity context

## Business workspace reauthentication (2026-10-14)

Local slots distinguish real email and workspace identity. Reimporting one
Business member updates that member's credentials; another member of the same
workspace and the same email in a different workspace remain separate. Targeted
OAuth reauthentication rejects seat/workspace mismatches and replaces only the
matching slot. Explicit identity in opaque credential exports must survive a
round-trip, because the access token itself may have no decodable identity.

Per-workspace key scopes constrain account selection. They do not make existing
response anchors or encrypted compactions portable across account owners. Live
sign-outs, provider security policies and continuity across workspace switching
are not established by these local identity tests. Example: a1/a2 in workspace A
and a1 in B retain independent token material after reauthenticating A/a1.
See [requirements](spec.md) and
[account-routing](../account-routing/spec.md).
