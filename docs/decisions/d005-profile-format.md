---
type: Decision
title: D-005 — Minimal Markdown-First Engineering Profile
status: stable
tags: [profile, format, architecture]
---

# Context

We want engineering artifacts that are portable and human-readable, with Battalion as an initial reference producer but never as a dependency. OKF v0.3 already supports metadata, provenance, lifecycle, links, and producer-defined extensions.

# Decision

**Decision ID:** D-005. **Approval:** accepted.

- Build the Engineering Profile on OKF v0.3 Markdown with YAML frontmatter.
- Introduce only engineering type names, small body-heading conventions, and demonstrated metadata extensions.
- Reuse OKF `sources` for origin; permit the optional source-entry `x-lattivra-revision` when an exact source revision is not conveyed by an immutable URI.
- Keep source revision declaration distinct from actual source-content verification.
- Do not import producer-specific approval, workflow, or execution authority.

# Rationale

Reusing OKF avoids format fragmentation and limits tooling requirements. Battalion's canonical structured records can be published as OKF Markdown projections without making the projections authoritative over Battalion's own state.

# Consequences

- Profile validation must be possible independently of Battalion.
- More elaborate schema frameworks and typed relationships are deferred.
- Authors need only text editors to produce the format.
- Source-revision metadata is an opaque assertion until separately checked by an appropriate resolver.

# References

- [Engineering Profile](../../profiles/engineering/profile.md)
