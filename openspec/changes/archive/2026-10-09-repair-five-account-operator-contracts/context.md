## Scope and examples
Exactly five registry records. A backup with source ID `old-id` imports as `new-id`: settings apply to `new-id`, including an explicit empty alias and disabled warm-up. A 50% operator cap prevents admission at 50% even if an upstream-specific quota exemption or error-backoff fallback is used.

## Decisions and failure modes
Paused accounts remain observable but cannot redeem or poll. Bulk redeem obtains actual remaining IDs after a consume; if the next observation fails, the batch retains completed counts and continues to other accounts. A 50% reset warm-up threshold accepts a before sample of 50% and rejects 49%; zero accepts any confirmed reset. Historical legacy threshold values are retained but inactive.

## Constraints
No new environment configuration or dependency. Contract tests use synthetic credentials and isolated databases. External provider, production, full upstream reserve accounting and browser screenshots are not certified by focused tests.

A compatible active column surviving a rewound ledger is verified and reused without changing its current value. Incompatible nullable/type/default shapes fail explicitly. Paid-to-Free zero-floor semantics are preserved; positive floors require a matching monthly baseline.
