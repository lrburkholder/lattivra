---
type: Decision
title: D-004 — Defer Indexing Engine Selection After the M0 Catalog Evaluation
status: stable
tags: [explorer, indexing, deferred, m0]
---

# Context

The Explorer requires search across registered OKF bundles, reliable retrieval of each hit, and rebuildable links and backlinks. M0 tested the Open Knowledge Catalog (OKC) v0.1.0 Windows release against the same fixture corpus used by the independent reader. [Candidate evaluation](../compatibility/open-knowledge-catalog.md)

# Decision

**Decision ID:** D-004. **Approval:** accepted decision to defer selection.

Continue to defer engine selection. M0 recommends against adopting OKC v0.1.0 as-is. Keep the existing reader for file-based profile validation. Defer both an OKC adapter and an independent indexer until there is a concrete need for cross-bundle search.

# Rationale

OKC preserved source bytes and exposed provenance and extension fields. Its combined index lost the distinction between two documents at the same native path. An edit left old text searchable, and deleting a target left a surviving link marked valid. A rebuild from identical inputs produced different search and backlink data. These failures affect which document a user opens and whether its references can be trusted.

One database per registration isolated the two decisions in the test. An adapter would still need to merge searches, route hits, normalize Windows paths, and repair stale entries and backlinks. Relying on the private SQLite schema would add migration work with each upstream change. The fixture reader provides an independent reference for these semantics. Its search performance and the cost of extending it into an indexer remain unmeasured. [Adaptation cost and license](../compatibility/open-knowledge-catalog.md#adaptation-cost-and-license)

# Consequences

- Do not couple Explorer application APIs to a candidate indexer's internal storage model.
- No permanent indexing dependency, database schema, or programming language is approved by this decision.
- Keep derived state disposable. Native Markdown and the upstream records behind projections retain their respective authority.

# Revisit Trigger

When indexing work resumes, run the same fixture and add/edit/delete sequence against a pinned candidate and a small independent implementation. Require correct retrieval of both shared decisions, removal of stale text and edges, and equivalent refresh and rebuild results on the intended platforms. Compare the maintenance cost before selecting an engine. [M0 findings](../compatibility/m0-findings.md)

# References

- [M0 compatibility plan](../plans/m0-compatibility.md)
- [D-006 cross-source identity](d006-cross-source-identity.md)
- [D-007 bundle discovery](d007-bundle-discovery.md)
