## Implementation

- [x] Preserve the existing MySQL selection in one canonical manifest.
- [x] Add MySQL weighted file-group selection and validation to the sharder.
- [x] Add three local shard targets while preserving the full MySQL target.
- [x] Add the CI matrix, duration artifacts and strict compatibility aggregate.
- [x] Cover partition integrity, selector validation and required contexts.
- [x] Run the requested unit tests, shard validation, lint and strict OpenSpec validation.
- [x] Verify all three Make targets against MySQL 8.4 with two isolated xdist workers.

## Publication follow-up

After the verified implementation is published to main, collect GitHub job and
workflow timestamps and compare them with the recorded baseline. Store the
run-specific measurements and logs in the ignored `.test-results/` directory;
they are execution evidence rather than normative requirements.
