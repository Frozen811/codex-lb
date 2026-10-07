## Scope

Exactly UP-PR-2449, UP-PR-2439, UP-PR-2440, UP-PR-2403, and UP-PR-2391 were unverified at baseline `205e9c54bbab433c2621378e5c05a86f2fd253cb`. Live GitHub inspection on 2026-10-07 found 2449 merged and the other four open. PR 2391 is a library contract; its pool-walk integration follow-up is outside its original scope.

## Rationale and constraints

A quota reset serves two consumers: the client's terminal failure and the account-health deadline. Discarding invalid numeric metadata must not discard the original failure, authorize cross-account replay, or bypass keyed settlement. No additional settings or dependencies are needed.

## Example and failure modes

An upstream frame with `code: usage_limit_reached`, `resets_at: NaN`, and `resets_in_seconds: 432000` must retain the code and relative reset, omit the invalid absolute reset, and render successfully. A finite reset remains visible. An `invalid_request_error` message quoting "The usage limit has been reached" remains a request error and does not bench the account.

## Verification boundary

Focused local routes, typed parsing, account persistence, and library tests use synthetic upstream responses. The user authorized a local commit on `main`; publication, cloud CI, release, and production are separate scopes.
