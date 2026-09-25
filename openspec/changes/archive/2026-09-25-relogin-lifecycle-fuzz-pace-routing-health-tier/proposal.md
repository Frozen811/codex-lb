# Proposal: relogin-lifecycle-fuzz-pace-routing-health-tier

## Summary
Resolve Batch 41 (Tasks 151–154) completing the remaining issues in `ISSUES.md`:
- **Task 151 (Issue #1959)**: Decoupled automated re-login lifecycle and audit notifications (`account_reauth_required` audit event for external headless reauth runners, adhering to P1/P2 simplicity principles by rejecting in-core browser dependencies).
- **Task 152 (Issue #1595)**: Property-based fuzz testing using `hypothesis` to verify balancer state machine and routing safety invariants across arbitrary state inputs.
- **Task 153 (Issue #956)**: Pace-aware routing in load balancer to land usage smoothly on reset boundaries and prevent premature window exhaustion.
- **Task 154 (Issue #578)**: Eliminate health-tier overlap in budget-safe account selection so degraded accounts cannot leapfrog healthy accounts simply by having lower usage.

## Capabilities Touched
- `account-identity`
- `account-routing`
- `deterministic-proxy-simulation`

## Impact & Simplicity
- 0 new `CODEX_LB_*` settings (97/97 budget strictly maintained).
- Zero modifications exceeding file length limits in sensitive modules.
- 100% test coverage with focused unit and property-based test suites.
