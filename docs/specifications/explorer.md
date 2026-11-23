---
type: Specification
title: Lattivra Explorer — Initial Requirements
status: draft
tags: [explorer, mvp, requirements]
---

# Context

A developer's OKF documents may be distributed among multiple repositories and local directories. A general-purpose local-first browser should make those documents searchable, navigable, and inspectable without moving or editing them. The Engineering Profile is optional.

# Requirements

## Sources and discovery

- EXP-001: Support configuring multiple local search locations.
- EXP-002: Support enabling/disabling configured locations and explicitly registering one or more bundle roots beneath a source directory.
- EXP-003: Identify the source and relative concept path for each indexed artifact.
- EXP-004: Never change source files during discovery or indexing.
- EXP-005: Respect exclusions, filesystem permission boundaries, and the OKF rule excluding dot-prefixed paths.
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

## Identity

- Preserve OKF's bundle-relative concept IDs. Maintain an Explorer-local persistent source/bundle registration identity for indexing.
- By default, exclude an explicitly registered child bundle subtree from its registered parent bundle to avoid double indexing.
- Never identify two concepts as equal just because their concept paths or declared upstream provenance match.

# Acceptance Criteria

1. Two separate fixture bundle roots, including duplicate concept paths, are indexed with distinct Explorer identities.
2. A document can be found by text search and browsed by source/type.
3. Relative, bundle-root, unresolved, and explicitly mapped cross-bundle links behave deterministically.
4. Invalid documents remain diagnosable; their presence does not block good documents.
5. The source files remain unchanged after discovery, indexing, and navigation.
6. Ordinary OKF content is viewable with no Engineering Profile installed.

# Non-Goals

No editing, remote sources, cloud sync, MCP integration, execution engine, or mandatory graph visualization in the initial release.

# Related Plans

- [M0 compatibility POC](../plans/m0-compatibility.md)
