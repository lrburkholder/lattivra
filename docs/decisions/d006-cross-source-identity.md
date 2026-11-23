---
type: Decision
title: D-006 — Bundle-Scoped Identity and Conservative Cross-Source Resolution
status: stable
tags: [identity, links, explorer]
---

# Context

OKF concept IDs are relative paths within a bundle, so distinct bundles may contain the same ID. Explorer must not conflate them. External links may reference configured local material, but matching cannot be inferred solely from filenames.

# Decision

**Decision ID:** D-006. **Approval:** accepted as the M0 design baseline; exact implementation is pending testing.

- Preserve native OKF bundle-relative concept IDs.
- Assign persistent Explorer-local identifiers to explicit bundle registrations; qualify index identities with registration ID and concept path.
- Resolve local Markdown links and OKF path fields according to the normative specification.
- Map cross-bundle URI targets only with explicit mappings and only when a unique match exists. Otherwise retain the external reference or report ambiguity.
- Treat source revision provenance as informational, not as an Explorer concept ID.

# Rationale

This avoids mandatory global IDs, custom URI schemes, accidental collisions, and false-positive relationships.

# Consequences

- A bundle move can preserve local Explorer registration identity by updating its configured path.
- A duplicate concept path across bundles is not a conformance error.
- A broken link remains visible and does not invalidate its originating concept.
- Automatic cross-source guessing is not a supported behavior.
