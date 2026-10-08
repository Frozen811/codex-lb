# Credential and quota recovery boundary

Scope: five selected records 2429, 2120, 2132, 2119 and 2326. Live GitHub bodies and heads were read on 2026-10-08. The initial candidate issue 2327 was excluded before coding because its public probe recovery requires a separate migration and distributed claim design; its registry row remains untouched.

Guardian protects idle refresh credentials independently of request freshness. For example an active account last refreshed thirteen hours ago remains fresh for an ordinary request but must receive a leader-owned guardian exchange. Paused accounts may exchange tokens while remaining unroutable.

Credits require capacity evidence. A weekly window at 100% with credits_has=true and balance=0 stays unavailable; balance=12.5 or unlimited credits can cover secondary exhaustion. Primary exhaustion and operator-disabled states retain the existing gates.

Recovery never grants operator authority to a late network result: a deletion marker defeats a preflight fallback, and accepted refresh-only warnings do not weaken proven access rejection. Retained reset history is evidence for the existing durable warmup claim, subject to current opt-in and availability.

Local tests use synthetic provider responses and isolated databases. No live provider, release, CI or production operation follows from this batch.
