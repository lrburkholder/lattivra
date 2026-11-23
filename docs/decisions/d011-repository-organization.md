---
type: Decision
title: D-011 — Single Monorepo with Independent Components
status: stable
tags: [foundation, repository, architecture]
---

# Context

Lattivra Explorer and the optional Engineering Profile have distinct responsibilities but are both at an early stage. Shared compatibility fixtures and architecture documentation will be useful during development. The project is maintained primarily as a personal portfolio and learning project.

# Decision

**Decision ID:** D-011. **Approval:** accepted.

Use a single repository initially, with the Explorer and Engineering Profile maintained as separately usable components. Host the repository in the maintainer's personal GitHub account when created; no separate organization is needed at bootstrap.

# Rationale

A monorepo keeps related test fixtures and standards discussions together without demanding cross-repository release coordination at this stage.

# Consequences

- Keep profile conformance independent of installing or running Explorer.
- Keep Explorer core OKF support independent of the optional Engineering Profile.
- Allow independent component versioning and releases if needed.
- Revisit separation only if release cadence, contributors, or independent adoption justify it.

# References

- [D-001 project name](d001-foundation.md)
- [D-005 profile format](d005-profile-format.md)
