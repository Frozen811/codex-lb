# HTTP phase and abrupt-drop evidence

Scope is exactly UP-ISSUE-2169, UP-ISSUE-2108, and UP-ISSUE-2074. A phase is an observed event at the service attempt boundary, not TCP first byte or client receipt. For example, a 500 ms admission wait followed by metadata at 250 ms, created at 500 ms and text at 1000 ms must persist those attempt offsets, plus a separate 500 ms queue value.

A local timeout frame is not upstream activity. An upstream error with a synthesized local response ID is still upstream activity. Keepalive/comment blocks provide neither phase. A post-output frame-less bridge ending still fails the request without replay or account penalty; only eventless drops feed the existing repeated-drop drain signal.

The native fixture releases its bound socket before attempting the refused endpoint. A bound non-listening socket is not a portable refusal condition. Verification must preserve all four SSE outcomes and both compact outcomes under their existing bounds. Live macOS/provider/production evidence is separate.
