---
type: Decision
title: D-007 — Explicit Bundle Roots Under Configured Sources
status: stable
tags: [discovery, bundles, explorer]
---

# Context

One filesystem directory may contain several independent OKF bundles. An `index.md` in an ordinary subdirectory does not automatically mark it as a separate bundle. Overlapping bundle registrations can otherwise duplicate the same physical files.

# Decision

**Decision ID:** D-007. **Approval:** accepted.

- Users configure source directories and explicitly register one or more bundle roots within those directories.
- The MVP rejects duplicate roots and overlapping roots where one contains another. Compare resolved filesystem locations so aliases cannot register the same tree twice.
- Reject a proposed conflicting registration with a configuration diagnostic naming both roots and leave previously accepted registrations unchanged.
- Scan each accepted bundle according to its native OKF boundary. An unregistered nested `index.md` does not exclude that subtree or change link resolution.
- Support for overlapping registrations and automatic bundle-root detection is deferred.

# Rationale

Explicit, non-overlapping boundaries make concept IDs and link resolution predictable while keeping compatibility with the OKF bundle definition. Excluding a registered child subtree from its parent would require additional rules for parent links into that subtree, concept ownership, and backlinks; the MVP avoids that ambiguity.

# Consequences

- Initial configuration is slightly more manual.
- Users must choose either the parent bundle or separate child bundles when their roots overlap.
- Registration conflicts are configuration errors, not OKF conformance failures in the source bundles.
- An unregistered nested `index.md` alone does not create an independent bundle identity.

# Revisit Trigger

Revisit overlapping registrations only when a concrete use case justifies specifying concept ownership, parent-to-child link resolution, backlinks, and identity stability as registrations change.
