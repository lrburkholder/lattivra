# M0 fixture inventory

All content is synthetic. The projected requirement uses an invented Battalion-style URI and revision; no private data or Battalion runtime is required.

The authoritative expected outcomes are in [corpus.json](corpus.json). The CLI compares the complete discovered document/asset inventory, each document's kind, selected profile result, diagnostics (including duplicates), and reference outcomes against that file. Changes to expectations require review; the harness never updates them automatically.

The `.bundles/` directory is deliberately hidden from the containing repository's OKF scan. The individual roots beneath it are explicitly registered in the corpus. This keeps deliberately malformed fixtures from making Lattivra's own documentation bundle invalid. Tests create filesystem aliases in temporary directories instead of checking platform-specific symlinks into Git.

| Registered root | Expected result |
| --- | --- |
| `.bundles/alpha` | Discover seven concepts, including all three profile types, a native record, a projection, and an unfamiliar type. Three malformed files fail format checks; neighbors remain readable. The generic Decision fails only selected profile checks. Broken/ambiguous references are nonfatal diagnostics. Hidden files are excluded; the ordinary nested index does not split the bundle. |
| `.bundles/beta` | Independent conformant bundle with the same `decisions/shared` ID as alpha. Profile checks are not applied. An explicit URI mapping can resolve to this concept. |
| `.bundles/unsupported` | Retain the version warning while consuming its concept using best-effort behavior; no structural format failure. |
| Attempted alpha child and beta duplicate registrations | Reject both with configuration diagnostics; accepted bundles remain unchanged. |

`test_m0.py` adds parameterized temporary cases for parsing, reserved files, optional metadata, timestamps, lifecycle, path fields, legacy path fallback, static computation discovery, registration conflicts, and filesystem escapes. Each test references checklist IDs through the `contract` marker where applicable.

See [the harness guide](../../docs/compatibility/m0-harness.md) for commands, result dimensions, coverage limits, and CI behavior.
