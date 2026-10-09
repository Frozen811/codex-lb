# API Firewall Context

## Plugin catalog URL parity

The [plugin alias requirement](spec.md#requirement-plugin-catalog-aliases-share-firewall-enforcement)
protects catalog reads that spend pool credentials. For example,
`/backend-api/plugins/featured/` and `/plugins/featured` apply the same
IP allowlist before selection. Backend-api aliases and trailing slashes do
not provide a bypass. The existing empty-list allow-all and trusted-peer
contracts remain authoritative. Controlled ASGI tests cover every catalog
alias with an excluded client address; this does not certify a live reverse
proxy or production firewall.
