## Context

The browser job restored the pinned Chromium cache successfully, then entered `playwright install --with-deps chromium`. Its log stopped during apt-get metadata acquisition from Ubuntu mirrors at 18:10 UTC on October 7 and resumed only with cancellation at 00:11 UTC on October 8. No explicit job or installation-step timeout was configured. See the proposal for the affected CI result.

## Decisions

Use native GitHub job/step deadlines, retaining a ten-minute installation allowance within a twenty-minute job budget. Configure APT's own acquisition timeouts and retries in `/etc/apt/apt.conf.d/99-codex-lb-ci-network`; Playwright invokes apt-get through sudo, so a runner-local APT configuration file remains effective across that privilege boundary. APT settings apply only to the disposable job runner.

Keep browser and OS dependency installation mandatory even on cache hits. Do not use continue-on-error, cached-browser bypasses, or altered aggregate conditions. The existing CI Required dependency keeps an installation failure visible. Browser download defaults remain unchanged because the observed stall was in APT, not the Chromium download.

## Risks / Trade-offs

- A slow/unreachable mirror now fails within the configured bounds rather than consuming the six-hour default; acquisition retries cover temporary failures and the actual full cloud run verifies the successful path.
- APT cannot cover every source of process hangs, so the native step and job deadlines remain the outer bounds.
- The GitHub runner image and actual mirror network cannot be reproduced exactly on Windows; focused YAML regressions and a disposable Ubuntu APT parser check cover local behavior, followed by real cloud CI.
