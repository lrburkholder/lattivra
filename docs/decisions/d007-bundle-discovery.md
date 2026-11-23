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
- Nested registered bundles are supported as independent bundles.
- By default, a registered child-bundle subtree is excluded from an overlapping registered parent bundle's scan.
- The Explorer reports overlaps clearly; automatic bundle-root detection is deferred.

# Rationale

An explicit boundary makes concept IDs and link resolution predictable while keeping compatibility with the OKF bundle definition.

# Consequences

- Initial configuration is slightly more manual.
- No files are indexed twice by default under overlapping registrations.
- An unregistered nested `index.md` alone does not create an independent bundle identity.
