## Context

The five selected records describe an existing pipeline. Terminal renderers convert `resets_at` to an integer, while `OpenAIError` currently accepts non-finite floats. A malformed upstream value can therefore replace a quota failure with a Python exception. The Responses spec also disagrees with the already implemented request-error protection.

## Goals / Non-Goals

Preserve finite reset numbers and the original quota failure, verify every selected consumer, and align the normative text. Pool selection, retry limits, ownership, settlement ordering, and reset-horizon policy remain governed by their existing contracts.

## Decisions

Use one numeric guard in `app/core/errors.py` for public error construction and the typed upstream error model. Accept integers and finite floats; reject booleans and non-numeric values. Apply model validation after strict numeric parsing, preserving the existing fallback parser's numeric-string handling. Keep implausible but finite horizons available to the existing account-health policy.

Drive real Responses routes in integration tests, using only synthetic upstream I/O. Existing last-account, visible-output, original-terminal, keyed settlement, and pool-bound tests provide independent verification; add malformed metadata cases and a request-content echo negative control where the failing route needs it.

## Risks / Trade-offs

- Invalid metadata loses its retry hint: preserve the quota code/message and use the existing metadata-free health fallback.
- Strict numeric behavior could accidentally change numeric-string compatibility: retain parser fallback behavior and cover it explicitly.
- Focused local evidence cannot certify real upstream wording, production, or cloud CI: record these limits in the registry and verification report.
