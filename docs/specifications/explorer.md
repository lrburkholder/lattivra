---
type: Specification
title: Lattivra Explorer — Initial Requirements
status: draft
tags: [explorer, mvp, requirements]
---

# Context

A developer's OKF documents may be distributed among multiple repositories and local directories. A general-purpose local-first browser should eventually make those documents searchable, navigable, and inspectable without moving or editing them. The Engineering Profile is optional.

This specification defines **future Explorer functionality**, not an M0 delivery requirement. Standalone UI implementation and platform evaluation are deferred under [D-003](../decisions/d003-explorer-platform.md) until Battalion can support creating that UI. The Engineering Profile and OKF compatibility tooling remain useful independently of the Explorer.

# Requirements

## Sources and discovery

- EXP-001: Support configuring multiple local search locations.
- EXP-002: Support enabling/disabling configured locations and explicitly registering one or more bundle roots beneath a source directory.
- EXP-003: Identify the source and relative concept path for each indexed artifact.
- EXP-004: Never change source files during discovery or indexing.
- EXP-005: Respect exclusions, filesystem permission boundaries, and the OKF rule excluding dot-prefixed paths. Do not follow symbolic links or filesystem aliases outside the registered bundle root during discovery, indexing, or navigation.
- EXP-006: Discover valid OKF `.md` concepts, not arbitrary Markdown files lacking `type`.

## Index, search, and links

- EXP-007: Index frontmatter and searchable Markdown body content.
- EXP-008: Rebuild derived indexes from original sources.
- EXP-009: Detect added, changed, and removed artifacts on refresh.
- EXP-010: Report malformed artifacts while continuing to index valid artifacts.
- EXP-011: Search across every enabled registered bundle.
- EXP-012: Filter by source and artifact type.
- EXP-013: Follow ordinary OKF Markdown links and supported path fields.
- EXP-014: Show backlinks derived from indexed references.
- EXP-015: Report unresolved and ambiguous references without inventing a target.
- EXP-016: Resolve external URI references to another configured bundle only when an explicit mapping is unique.

## Presentation and safety

- EXP-017: Render Markdown safely without executing untrusted content.
- EXP-018: Display structured metadata distinctly from the Markdown body.
- EXP-019: Display available provenance, lifecycle, and verification information without elevating it to application authority.
- EXP-020: Display actionable parsing/validation diagnostics.
- EXP-021: Allow opening or locating the original file.
- EXP-022: Apply Engineering Profile checks only when explicitly selected for a bundle or standalone validation run. A matching type name alone does not select the profile; show checks as not applied outside the selected scope.

## Identity

- Preserve OKF's bundle-relative concept IDs. Maintain an Explorer-local persistent source/bundle registration identity for indexing.
- Reject duplicate and overlapping registered roots in the MVP, comparing resolved filesystem locations. Report both conflicting roots and leave previously accepted registrations unchanged.
- An unregistered nested `index.md` does not change the containing bundle's boundary or link resolution.
- Never identify two concepts as equal just because their concept paths or declared upstream provenance match.

# Acceptance Criteria

1. Two separate fixture bundle roots, including duplicate concept paths, are indexed with distinct Explorer identities.
2. A document can be found by text search and browsed by source/type.
3. Relative, bundle-root, unresolved, and explicitly mapped cross-bundle links behave deterministically.
4. Invalid documents remain diagnosable; their presence does not block good documents.
5. The source files remain unchanged after discovery, indexing, and navigation.
6. Ordinary OKF content is viewable with no Engineering Profile installed.
7. The same generic `Decision` document receives no profile diagnostics when checks are not selected; selecting the Engineering Profile applies its required headings without changing the document's OKF conformance result.
8. Refresh reflects additions, edits, and deletions in search and backlinks. A clean rebuild from the same sources and registration configuration produces equivalent concepts, references, and search results with the same concept identities.
9. Conflicting registrations produce configuration diagnostics without changing accepted registrations; links into ordinary unregistered subdirectories retain native OKF resolution.
10. Symbolic links or aliases escaping a bundle root are not traversed, and blocked targets have actionable access diagnostics.

# Non-Goals

No editing, remote sources, cloud sync, MCP integration, execution engine, or mandatory graph visualization in the initial release. No standalone UI implementation or UI framework evaluation during M0.

# Related Plans

- [M0 compatibility POC](../plans/m0-compatibility.md)
