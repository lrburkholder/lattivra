# M0 fixture inventory

All content is synthetic. The two projected requirements use invented Battalion-style URIs and can be read offline. Alpha records the opaque revision `synthetic-revision-007`. Beta omits the optional revision. Both name the same fixture exporter and generation time.

The CLI checks the discovered documents and assets against the expected inventory. Each document records its kind. An omitted profile result means checks are unselected or inapplicable. Omitted diagnostics and references mean none are expected. A reference can specify a state alone, such as `unresolved`, or a state and a bundle-qualified destination. [Fixture expectations](corpus.json)

The `.bundles/` directory is deliberately hidden from the containing repository's OKF scan. The individual roots beneath it are explicitly registered in the corpus. This keeps deliberately malformed fixtures from making Lattivra's own documentation bundle invalid. Tests create filesystem aliases in temporary directories instead of checking platform-specific symlinks into Git.

| Registered root | Expected result |
| --- | --- |
| `.bundles/alpha` | Discover seven concepts, including all three profile types, a native record, a projection, and an unfamiliar type. Three malformed files fail format checks; neighbors remain readable. The generic Decision fails only selected profile checks. Broken/ambiguous references are nonfatal diagnostics. Hidden files are excluded; the ordinary nested index does not split the bundle. |
| `.bundles/beta` | Discover two concepts with profile checks unselected. The projection links to beta's own `decisions/shared`. Alpha's mapped URI also resolves to that decision. |
| `.bundles/unsupported` | Retain the version warning while consuming its concept using best-effort behavior; no structural format failure. |
| Attempted alpha child and beta duplicate registrations | Reject both with configuration diagnostics; accepted bundles remain unchanged. |

The backlink tests read incoming edges for each decision separately. Alpha's decision has three referring concepts within alpha (the native specification, nested concept, and unknown type). Beta's decision has a local link from its projection, a mapped body link from alpha's native specification, and a self-reference through its own mapped `resource`. Alpha's broken and ambiguous links contribute no edges.

`test_m0.py` adds parameterized temporary cases for parsing, reserved files, optional metadata, timestamps, lifecycle, path fields, legacy path fallback, static computation discovery, registration conflicts, and filesystem escapes. Each test references checklist IDs through the `contract` marker where applicable.

See [the harness guide](../../docs/compatibility/m0-harness.md) for commands, result dimensions, coverage limits, and CI behavior.
