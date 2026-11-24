---
type: Specification
title: Lattivra Foundation and Interoperability
status: draft
tags: [foundation, interoperability]
---

# Context

Lattivra is an independent portfolio and learning project with two separately usable components: a general-purpose Explorer and an optional Engineering Profile. Battalion is an anticipated primary producer and consumer, not a dependency or governing authority. The Engineering Profile and OKF compatibility work provide value before a standalone Explorer UI exists.

# Requirements

- The project MUST use OKF v0.3 as the intended format baseline for M0 fixtures and documentation.
- The Explorer MUST function without the Engineering Profile.
- The Engineering Profile MUST be usable without the Explorer or Battalion.
- Registered source files MUST remain unchanged in their original locations; indexes and search data are rebuildable derivatives of those inputs.
- Native Markdown artifacts MAY be authoritative records. A Markdown projection MAY instead derive from an authoritative upstream record; indexing the projection MUST NOT elevate it over that upstream record.
- Core Explorer operation MUST be local-first and not require cloud services.
- The first Explorer release MUST be read-only with respect to artifact source files.
- Standalone Explorer UI implementation and UI framework evaluation are deferred until Battalion can support creating that UI. Neither the Engineering Profile nor M0 compatibility deliverables require the UI.
- Battalion MAY generate or consume conforming profile artifacts without requiring Lattivra Explorer; its own authoritative data and approval semantics remain Battalion's responsibility.
- An imported artifact MUST NOT be treated as executable instructions, a trusted statement, or application authorization merely because its syntax is valid.
- The project SHOULD favor reuse of prior art when integration cost is justified, but may choose educational implementations deliberately.

# Acceptance Criteria

1. A standalone producer can author a conforming profile document without importing any Lattivra code.
2. Two independent bundles can be indexed and inspected without modifying their source files.
3. Unrecognized types and extensions do not invalidate an otherwise conformant OKF bundle.
4. Technical decisions are documented as profile-compliant Markdown concepts.
5. A projected artifact can retain its declared upstream authority while Explorer reads the projection without modifying either source or treating the index as authoritative.

# Non-Goals

Building an orchestration system, replacing Git, executing embedded instructions, implementing a knowledge lifecycle service, integrating Battalion during M0, or delivering a standalone Explorer UI during M0.

# Related Decisions

- [D-005](../decisions/d005-profile-format.md)
- [D-006](../decisions/d006-cross-source-identity.md)
- [D-007](../decisions/d007-bundle-discovery.md)
