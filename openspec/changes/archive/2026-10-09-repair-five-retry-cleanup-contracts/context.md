This local batch covers exactly UP-PR-2280, UP-PR-2276, UP-PR-1962, UP-PR-2345 and UP-PR-2278. Fresh GitHub source metadata and patches are captured in source-snapshot.json. Upstream PR state is provenance rather than local acceptance evidence.

For example, a candidate selected as `stream_incomplete` can become `anchor_superseded` without a timestamp/count/generation change. Removing it with the old snapshot erases protection that this cleanup never observed. Comparing its selected detail preserves it; keyset progression still removes unrelated stale rows.

The other entries concern completion authority, session replacement, local evidence deadlines, exclusive probe return and reason-only incomplete terminals. Existing runtime code is verified with route and lifecycle coverage. Upstream unresolved overflow and deadline-only probe policies are not adopted by closing the tested local contracts.
