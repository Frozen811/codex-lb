## Context

The relay polls one owned downstream receive task while the upstream reader runs independently. Clean upstream retirement can await socket closure/account-lease cleanup between polling iterations. During that await, a downstream task can complete. The existing `None or done()` recreation condition overwrites it, so a queued turn or disconnect can be lost.

## Decisions

Retain the receive task until the existing result-consumption `finally` clears ownership. Only `None` permits creation of a replacement. Explicit lifecycle cancellation/idle shutdown retains its existing cancel-and-await behavior.

For deterministic coverage, the first upstream close frame waits until the second downstream receive has started. Retiring that upstream releases the second message and waits for it to become ready before handoff returns. The unchanged three-second test bound must then see two upstream connections, exactly four lifecycle frames, and both completed IDs. Also run existing disconnect/drain/replay/clean-close controls.

## Risks / Trade-offs

Completed receive exceptions and disconnects now reach the normal handling path instead of being silently replaced. A cancelled lifecycle remains governed by existing teardown; this change adds no send or migration authorization.
