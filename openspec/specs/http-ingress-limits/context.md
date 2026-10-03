# HTTP ingress limits context

See [spec.md](spec.md) for the body admission contract. Global middleware bounds
ordinary ingress; route-owned readers may impose smaller budgets.

## SCIM admission

SCIM POST, PUT, and PATCH resource writes share a 64 KiB reader. Declared length
is only a claim: the actual stream is counted before appending each chunk,
and the tail is left unread after a crossing chunk. Existing users and new
account state stay unchanged after admission refusal.

The SCIM declared-length precheck compares a zero-stripped ASCII decimal
string to the short decimal budget. Converting arbitrary input with `int()`
could raise for more than the runtime's permitted digit count, and `isdigit()`
also recognizes characters such as the Latin-1 superscript two that `int()`
does not parse. Rejecting nondecimal syntax with the SCIM 400 envelope and
oversized decimal lengths with SCIM 413 avoids both cases without changing the
streaming budget. Leading zeroes do not change numeric meaning.

For example, a length of `00065537` is refused before reading any body, while
`00065536` permits a valid JSON resource padded to exactly 64 KiB. A false
declared length of `1` cannot admit a larger stream. The same behavior holds
when a decimal header has thousands of leading zeroes.

These are route admission guarantees when a header reaches ASGI. HTTP servers
and reverse proxies can reject invalid framing earlier, using their own
transport error response. The verification uses synthetic SCIM credentials,
real application routes and isolated database writes, without an external
identity provider.
