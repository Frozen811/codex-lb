

## Fork account reserves completed on 2026-10-09

The prior scalar-only partial status is superseded by the completed reserve integration. Shared and duration-matched 5-hour/weekly caps use the canonical fresh-data evaluator; disabled settings retain saved percentages, while removal clears them. Provider remaining stays in provider units; reserved and usable quota are shown separately, and weekly burn remains provider-scaled. A 20% reserve with 54% consumption gives 46% provider remaining and 26% usable quota.

The fork adds a single forward revision on its verified reset-threshold head. Legacy positive scalar values seed the shared policy and zero remains a hard denial. The legacy API updates the shared policy; the reserve API can disable/remove it. Backup carries the shared and override values. MySQL updates use the transaction-held row lock and projection instead of UPDATE RETURNING.

Fresh owner authorization retains strict revoked-credential handling and usable reauth warning behavior for manual warm-up. Selection retries are bounded at eight to let local and persisted invalidation echoes settle, with final current-owner refusal and complete lease cleanup under continuing churn. Foreground ranking ignores unavailable peers when choosing the best health tier but retains their hard-block evidence for canonical backoff fallback.

Code and tests are adapted from NikitaMGrimm's upstream PR #1528 at caf31b77a4ef85047459635e956fdd62f7fbd7ce; aaravrav is credited there for complementary reserve presentation. No old migration or prior archived evidence is rewritten. Local verification is separate from live providers, server backends and publication. See [requirements](spec.md).
