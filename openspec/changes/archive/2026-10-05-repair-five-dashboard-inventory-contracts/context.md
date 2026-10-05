## Scope and examples

This batch processes exactly UP-PR-2565, UP-PR-2566, UP-PR-2576, UP-PR-2577 and UP-PR-2578. For example, filtering five loaded accounts to one active account leaves inventory total five; an image allowlist can contain `gpt-image-1` without making it available in Automations.

## Constraints and decisions

Keep detail view and current account sort defaults. No dependencies, environment controls, migrations, navigation additions or changelog edits. The warning uses existing count/expiry visibility settings and changes only presentation, not redemption policy. All browser screenshots and API tests use synthetic data.

## Failure modes and evidence

Test missing/non-finite quota, missing usage, invalid timestamps, storage denial, empty model catalog, source collisions, read-only controls and timer teardown. Preserve prior dirty file contents and record exact commands, source heads and residuals in verification.md before local registry closure. Local checks do not certify providers, public artifacts, production or current-head cloud review.
