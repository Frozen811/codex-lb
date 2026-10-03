INSTALL-12/13/14 cover the remaining installation channels. Public upstream chart URLs and `nix run github:Soju06/codex-lb` do not install this fork. Source builds let an operator choose an auditable checkout while public images remain historical.

Example failure: `helm install ... -f values-external-db.yaml --set externalDatabase.url=... --wait` leaves `wait-for-schema-head` running on an empty DB. The post-install Job is not created because Helm is still waiting for that pod to become Ready. A regular install Job removes the cycle without admitting traffic before schema head.

Official lifecycle reference: https://helm.sh/docs/topics/charts_hooks/ . Verification details and tool versions are recorded in verification.md and issues-check.md. No new settings or README sections are needed.
