---
type: Implementation Plan
title: M0 — OKF v0.3 Compatibility Proof of Concept
status: draft
tags: [m0, proof-of-concept, validation]
---

# Objective

Establish a verified technical baseline for parsing, indexing, searching, and navigating OKF v0.3 artifacts across separate bundles. Select a backend only after evidence from the fixture corpus. Do not start Explorer UI implementation before the POC.

# Tasks

[GitHub Issues](https://github.com/lrburkholder/lattivra/issues) is the operational task tracker. The work packages below describe the technical approach; track assignments, progress, and completion in issues. Keep architecture and reproducible experiment results in Markdown.

1. **Pin upstream contract:** Use the [pinned OKF v0.3 contract and conformance checklist](../compatibility/okf-v0.3-conformance.md) for the normative source, reviewed commit, and expected behavior for discovery, frontmatter, link resolution, lifecycle, and extensions. Map fixtures and tool results to its stable check IDs; keep unresolved interpretations visible.
2. **Build two standalone fixture bundles:** Include valid concepts of all three profile types, one native Markdown artifact, and one externally projected artifact with an optional `x-lattivra-revision`.
3. **Add negative and edge cases:** Duplicate concept paths across bundles, broken links, invalid YAML, missing frontmatter, unknown types and extensions, duplicate keys, relative/root links, outside-root paths, symbolic links escaping the bundle, optional metadata variations, and rejected duplicate/overlapping registrations under [D-007](../decisions/d007-bundle-discovery.md). Include an unregistered nested `index.md` and a generic `Decision` document lacking profile headings to test native discovery and explicit profile selection.
4. **Validate artifacts:** Apply [D-009](../decisions/d009-validation-policy.md): separate OKF conformance, explicitly selected profile conformance, version-compatibility warnings, reference diagnostics, and configuration/access diagnostics. Run profile checks both selected and not selected. An unknown `type` must remain valid OKF. Dynamic third-party profile loading is deferred under [D-010](../decisions/d010-external-profile-support.md).
5. **Evaluate Open Knowledge Catalog:** Test v0.3 parsing, source scanning, search, backlinks, path semantics, unknown fields, robustness, incremental refresh, and clean rebuilds. Add, edit, and delete fixture artifacts between read-only runs, then compare refreshed and rebuilt results using the same registration configuration. Document gaps, patches, maintenance risk, and license.
6. **Evaluate minimal alternatives:** Compare a small independent indexer and relevant existing OKF parsers against the observed gaps, not against assumptions.
7. **Record decisions:** Revisit [D-004](../decisions/d004-indexing-engine.md) after the POC results are available; revisit [D-003](../decisions/d003-explorer-platform.md) when compatibility evidence and learning objectives can inform platform selection.

# Verification

- Source artifacts are byte-for-byte unchanged by each discovery, indexing, refresh, rebuild, and navigation operation. Fixture edits between operations are explicit test setup; projected artifacts retain their declared upstream authority.
- Both registered fixture bundles are indexed independently, including identical concept paths.
- Search returns useful results across both bundles, with source attribution.
- Relative/root links, backlinks, explicit cross-source URI matches, ambiguities, and broken links have expected outcomes.
- Malformed artifacts produce diagnostics without blocking valid artifacts.
- Refresh adds new concepts, updates edited text and links, and removes deleted concepts and their outgoing backlinks. References to deleted targets become unresolved. Stale text, search entries, and backlink edges do not survive an edit or deletion.
- A clean rebuild from the same source state and registration configuration produces equivalent concept identities, metadata, references, diagnostics, and search matches. Persistent registration identities survive rebuilding the derived index; no identical search ranking or internal storage layout is required.
- A generic `Decision` without profile headings remains valid OKF. With no profile selected, its profile checks are not applied; selecting the Engineering Profile reports the missing headings as profile failures only.
- Duplicate and ancestor/descendant registration attempts are rejected without changing accepted registrations. Ordinary unregistered subdirectories remain part of their containing bundle, with unchanged relative/root-link resolution.
- Symbolic links and aliases escaping the bundle root are not traversed; blocked targets produce access diagnostics and valid concepts remain readable.
- `sources[].x-lattivra-revision` is preserved exactly when present and not interpreted as proof of authenticity.
- Findings include reproducible commands, expected/actual outcomes, and documented backend limitations.

## Fixture expectations

Record each fixture's expected and actual result independently for OKF conformance, selected profile checks, and reference/configuration/access diagnostics. Use not applied for unselected profile checks. At minimum, verify these distinctions:

| Fixture | Expected outcome |
| --- | --- |
| Invalid YAML or duplicate frontmatter keys | Frontmatter conformance failure; other valid concepts continue indexing. |
| Markdown without frontmatter or `type` | Skipped as a non-concept; no bundle conformance failure. |
| Unknown type or extension key | Accepted as ordinary OKF; unknown fields retained without a conformance failure. |
| Null, empty-string, and empty-list optional values; single-item forms of list fields | Consumed using OKF absent-value and singleton-list rules; no conformance failure. |
| Optional family entry missing its required key | Entry ignored with a warning; bundle remains conformant. |
| Unknown `status` or unparseable `stale_after` | Raw value retained with a warning; unknown status excluded from current-knowledge results and invalid staleness never shown as fresh. |
| Broken link or ambiguous explicit cross-source mapping | Reference diagnostic; no conformance failure or invented target. |
| Unsupported declared OKF version | Compatibility diagnostic and best-effort consumption. |
| Profile heading failure in an explicitly selected scope | Profile failure only; the same document outside that scope has profile checks not applied. |
| Duplicate/overlapping roots or an escaping symbolic link | Configuration or access diagnostic respectively; source conformance is reported separately. |

# Dependencies

- [Engineering Profile bootstrap](../../profiles/engineering/profile.md)
- [Explorer requirements](../specifications/explorer.md)
- [D-006 cross-source identity](../decisions/d006-cross-source-identity.md)
- [D-007 bundle discovery](../decisions/d007-bundle-discovery.md)
- [D-003 platform deferral](../decisions/d003-explorer-platform.md)
- [D-004 indexing deferral](../decisions/d004-indexing-engine.md)

# Exit Criteria

A working, repeatable POC reads two independent OKF v0.3 fixture bundles without mutating source files and documents results for every verification case above. Expected/actual fixture outcomes and refresh/rebuild evidence must be sufficient to select or reject the preferred indexing backend, with any remaining incompatibilities explicit in that decision.
