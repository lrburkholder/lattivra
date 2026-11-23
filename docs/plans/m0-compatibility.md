---
type: Implementation Plan
title: M0 — OKF v0.3 Compatibility Proof of Concept
status: draft
tags: [m0, proof-of-concept, validation]
---

# Objective

Establish a verified technical baseline for parsing, indexing, searching, and navigating OKF v0.3 artifacts across separate bundles. Select a backend only after evidence from the fixture corpus. Do not start Explorer UI implementation before the POC.

# Tasks

1. **Pin upstream contract:** Record the OKF v0.3 normative source, reviewed commit, and expected behavior for discovery, frontmatter, link resolution, lifecycle, and extensions.
2. **Build two standalone fixture bundles:** Include valid concepts of all three profile types, one native Markdown artifact, and one externally projected artifact with an optional `x-lattivra-revision`.
3. **Add negative and edge cases:** Duplicate concept paths across bundles, broken links, invalid YAML, missing frontmatter, unknown types and extensions, duplicate keys, relative/root links, outside-root paths, and explicitly overlapping registered bundles.
4. **Validate artifacts:** Apply [D-009](../decisions/d009-validation-policy.md): separate OKF conformance, optional profile conformance, version-compatibility warnings, and link-resolution diagnostics. An unknown `type` must remain valid OKF. Dynamic third-party profile loading is deferred under [D-010](../decisions/d010-external-profile-support.md).
5. **Evaluate Open Knowledge Catalog:** Test v0.3 parsing, source scanning, search, backlinks, path semantics, unknown fields, and robustness. Document gaps, patches, maintenance risk, and license.
6. **Evaluate minimal alternatives:** Compare a small independent indexer and relevant existing OKF parsers against the observed gaps, not against assumptions.
7. **Record decisions:** Revisit [D-004](../decisions/d004-indexing-engine.md) after the POC results are available; revisit [D-003](../decisions/d003-explorer-platform.md) when compatibility evidence and learning objectives can inform platform selection.

# Verification

- Source artifacts are byte-for-byte unchanged after indexing.
- Both registered fixture bundles are indexed independently, including identical concept paths.
- Search returns useful results across both bundles, with source attribution.
- Relative/root links, backlinks, explicit cross-source URI matches, ambiguities, and broken links have expected outcomes.
- Malformed artifacts produce diagnostics without blocking valid artifacts.
- `sources[].x-lattivra-revision` is preserved exactly when present and not interpreted as proof of authenticity.
- Findings include reproducible commands, expected/actual outcomes, and documented backend limitations.

# Dependencies

- [Engineering Profile bootstrap](../../profiles/engineering/profile.md)
- [Explorer requirements](../specifications/explorer.md)
- [D-006 cross-source identity](../decisions/d006-cross-source-identity.md)
- [D-007 bundle discovery](../decisions/d007-bundle-discovery.md)
- [D-003 platform deferral](../decisions/d003-explorer-platform.md)
- [D-004 indexing deferral](../decisions/d004-indexing-engine.md)

# Exit Criteria

A working, repeatable POC reads two independent OKF v0.3 fixture bundles without mutating source files and documents enough compatibility evidence to select or reject the preferred indexing backend.
