GitHub run 37577369205 at 352e58d9 completed in 6m07s with 33 successful
jobs. Firewall add/remove still timed out; 1748 other Vitest tests passed.
The existing timeout and all coverage thresholds are retained. Independent
add/remove cases each execute the real Settings route and API operations, with
separate mutable storage and auth initialization. The remove case additionally
asserts that opening confirmation does not delete and that confirmation is
disposed after deletion. The add case waits for the cleared input as well as
the persisted row. No failed test retry is introduced.

Large-page discovery uses the trigger's accessible label and the heading's
specific text selector, then explicitly asserts their roles and visibility.
This avoids repeated accessibility-name computations over unrelated Settings
controls while preserving accessibility checks for the actual targets.
Advanced expansion is checked separately from CRUD to give cold UI mounting
its own existing timeout budget rather than combining it with API interactions.

Focused coverage verification passed 9 tests in 14.08s; expansion/add/remove/
redirect interaction bodies took 5.163s/1.440s/1.695s/1.141s respectively.
Only this partial local coverage invocation disables whole-project minimums;
the committed full-suite coverage thresholds stay at 70%. Frontend lint and
typecheck passed, and strict validation passed all 68 canonical specs.
