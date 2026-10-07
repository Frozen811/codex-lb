# Verify five depth and quota contracts

## Why
The registry leaves F-082 and UP-ISSUE-2554/1918/1367 and UP-PR-2468 open. Existing fixes require current verification. Extension JSON can still bypass passthrough depth validation and fail during serialization.

## What Changes
- Bound opaque extra request fields at the same 200-container limit and preserve the offending field in HTTP 400 errors.
- Verify accepted boundary serialization, real database routing under concurrent leases, Edu exhausted quota, Team monthly API projection, and planner timezone rejection/fallback.
- Update only these five registry records with local evidence.

## Impact
Responses/chat request validation and focused regression coverage. No new settings, migration, UI layout, publication or deployment.
