## Context

The reader removes a matched terminal request from pending ownership and marks its settlement `claimed` before durable retry-circuit I/O. A reason-only incomplete has no response-created ID/event count on the request, and its queue can remain empty while that I/O opens the circuit. The stream's post-submit cooldown read currently treats this state as eventless and detaches the request, even though its terminal is already owned by the reader.

## Decisions

The post-submit empty-queue guard must additionally require no claimed terminal settlement and no observed upstream-terminal timestamp. The claim protects the interval before lifecycle timestamp updates; the timestamp protects the later interval when the claim has been settled. Keep the pre-submit admission check and the existing no-terminal negative control unchanged.

Delay the second reason-only incomplete after its real circuit write and synchronize post-submit checking with that delay. All three HTTP routes must receive the actual incomplete terminal while the durable count reaches two, duplicate receipt requests still avoid dispatch, reservations settle, and pressure drains. Unit controls separately exercise the claim and timestamp signals; the existing no-terminal negative control retains its cooldown refusal. Later admissions retain existing verified stale-anchor recovery policy.

## Risks / Trade-offs

The additional guards apply only after dispatch and actual upstream terminal ownership/evidence. They authorize neither a new send nor cross-account replay. If terminal processing aborts, existing bounded settlement/reader cleanup remains responsible for delivery and cleanup; the original no-terminal circuit refusal still detaches and fails closed.
