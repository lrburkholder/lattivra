---
type: Decision
title: D-004 — Defer Indexing Engine Selection Pending Compatibility Evidence
status: stable
tags: [explorer, indexing, deferred, m0]
---

# Context

The Explorer requires local discovery, metadata and full-text search, indexing across independent OKF v0.3 bundles, links and backlinks, actionable diagnostics, and rebuildable derived state. Open Knowledge Catalog is a promising existing project, but its exact v0.3 compatibility and suitability have not been demonstrated with Lattivra fixtures.

# Decision

**Decision ID:** D-004. **Approval:** accepted decision to defer selection.

- Make **no indexing-engine commitment** until the M0 compatibility proof of concept is complete.
- Evaluate Open Knowledge Catalog first as a candidate, not as the chosen backend.
- Compare its observed capabilities and adaptation cost with a small independent indexer and other relevant OKF parsing/indexing components.
- Keep the index rebuildable from unchanged registered source files. Native Markdown may be authoritative; a projection's upstream record may remain authoritative over the projection. The index does not replace either source.

# Rationale

A tool's feature list does not demonstrate accurate OKF v0.3 parsing, preservation of unknown fields, correct bundle path resolution, cross-source handling, or robust diagnostics. Testable evidence is preferable to selecting by perceived feature overlap.

# Consequences

- Do not couple Explorer application APIs to a candidate indexer's internal storage model.
- No permanent indexing dependency, database schema, or programming language is approved by this decision.
- Record reproducible fixture runs, observed compatibility gaps, dependency maintenance considerations, and license obligations during M0.

# Revisit Trigger

Select an engine only after the M0 report demonstrates behavior for multiple explicitly configured bundle roots, duplicate concept paths, malformed frontmatter, unknown types/extensions, links and backlinks, provenance, source-file immutability, and refresh/rebuild behavior. Document the rationale and any residual limitations in a follow-up decision or amendment.

# References

- [M0 compatibility plan](../plans/m0-compatibility.md)
- [D-006 cross-source identity](d006-cross-source-identity.md)
- [D-007 bundle discovery](d007-bundle-discovery.md)
