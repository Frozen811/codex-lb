## MODIFIED Requirements

### Requirement: Output speed sample evidence is preserved

New subscription-backed streaming logs MUST persist `latency_first_output_ms`, the first observed non-reasoning content time relative to the existing attempt/request-state anchor, and `output_delta_count`, the count of observed nonempty non-reasoning output chunks. Text, refusal and actual tool arguments/input MUST qualify; reasoning, metadata-only lifecycle events and empty deltas MUST NOT. These fields MUST remain nullable for historical and unsupported-source logs. Existing TTFT MAY still include visible reasoning or supported tool-start events and MUST be described as gateway-observed first output rather than model-internal or client end-to-end timing. Output sampling MUST use the event's actual content fields regardless of legal JSON key whitespace or escaping; unrelated nested fields MUST NOT create or hide output samples. Recording MUST preserve forwarded SSE bytes.

#### Scenario: Reasoning precedes actual output

- **GIVEN** a reasoning summary arrives at 200 ms and first text at 800 ms
- **WHEN** the request is logged
- **THEN** TTFT is 200 ms and first non-reasoning output latency is 800 ms
- **AND** TPS uses the non-reasoning output start

#### Scenario: Full terminal-only output

- **GIVEN** no streamed output has been observed and the terminal payload contains actual text or tool content
- **WHEN** that terminal event arrives
- **THEN** its receipt time may establish the first output and TTFT with one output chunk
- **AND** its TPS sample is insufficient
- **AND** positive usage alone MUST NOT synthesize first-output timestamps

#### Scenario: Equivalent JSON output fields retain the same sample

- **GIVEN** equivalent output delta events serialize their content keys with whitespace before the colon or JSON escapes
- **WHEN** the HTTP stream relays those events after TTFT is established
- **THEN** first output and output chunk counts match ordinary JSON serialization
- **AND** request-log and report generation speed use the same qualified sample

#### Scenario: Nested metadata does not establish output

- **GIVEN** an event has an empty content delta and a nonempty nested metadata field named `delta`
- **WHEN** that event is relayed
- **THEN** the nested field does not establish first output or increment output chunk count
