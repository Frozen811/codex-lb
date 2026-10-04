# Final source fingerprints

Base HEAD: 282ce147038ac53b72bca30d69c4ad9a9ac1b7cc. Local working-tree snapshot.

| Path | SHA-256 |
|---|---|
| app/modules/proxy/_service/http_bridge/retry_circuit.py | `d0771cf3f64142ed5a96721dfb545c970f19a403c46ec9a8512e2ea8ee459c2c` |
| app/modules/proxy/_service/http_bridge/request_submit.py | `e20af004f7262187225c2af12cda2ed467a074ad1e03a5480884ece79d08ee9e` |
| app/modules/proxy/durable_bridge_repository.py | `7b5dfdea849c41f618799fa66a120af2dd2fc41de0918bfc7bbe150261bf8cd8` |
| tests/unit/test_bridge_retry_claim_lifecycle.py | `d1c33bb6f1342daf7a6e7f00f4b27052eef0b7b2623245af10cadd8745f49b86` |
| tests/integration/test_bridge_retry_terminal_contracts.py | `54e801a45ffe634288b4dab8401b47ce62fa6e84c88a697bcd5b8b645bf2a366` |

Preservation: 94/94 unrelated original paths byte-identical; intended overlaps: issues-check.md, responses spec/context. Original spec/context retained as byte prefixes. Three source rows changed: UP-ISSUE-2273, UP-ISSUE-2272, UP-ISSUE-2271. Delta/main requirement blocks equal. Source rows: {"partial": 7, "locally_closed": 45, "unchecked": 245}.

Final combined run: 111 passed (43 new and 68 existing coordinator tests), with no skip/failure. Existing targeted run: 71 passed; overlapping counts are not aggregated.
