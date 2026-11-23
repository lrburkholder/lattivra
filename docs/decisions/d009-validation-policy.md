---
type: Decision
title: D-009 — Separate OKF Conformance, Profile Conformance, and Link Diagnostics
status: stable
tags: [validation, explorer, profile, m0]
---

# Context

Lattivra Explorer must index independent OKF bundles while the optional Engineering Profile applies stricter conventions to selected engineering artifacts. OKF v0.3 requires consumers to tolerate unknown types, extension metadata, and broken links. A single pass/fail result would conflate format correctness with optional profile rules and graph completeness.

# Decision

**Decision ID:** D-009. **Approval:** accepted as an initial validation policy; specific diagnostic codes and UI design remain implementation details to test in M0.

1. **OKF conformance:** Check bundle structure, reserved file conventions, and frontmatter parsing according to OKF v0.3. A `.md` file without frontmatter or `type` is not an OKF concept; skipping it is not a bundle conformance failure. Unknown `type` values and unknown extension fields are permitted. Distinguish normative failures from warnings or unsupported optional metadata.
2. **Optional Engineering Profile conformance:** For artifacts claiming one of the profile's three known types, check the bootstrap profile's required headings and optional extension-value rules. A profile failure does not imply an OKF conformance failure. A generic Explorer must work without loading this profile.
3. **Reference diagnostics:** Report unresolved links, ambiguous cross-source mappings, and unsupported external resolution separately from format or profile validity. Broken links do not invalidate OKF concepts.
4. **Unsupported versions:** Report a declared OKF version that the Explorer does not fully support as a compatibility diagnostic; attempt best-effort parsing per upstream guidance rather than automatically refusing the bundle.
5. **Isolation:** Continue indexing valid concepts when other files are malformed. Retain actionable file/field/location context for diagnostics where available; do not claim invalid documents were successfully indexed as valid concepts.

# Rationale

Separate diagnostic layers preserve native OKF semantics, allow third-party artifacts to remain useful, and avoid converting optional Lattivra conventions into universal requirements. Explicit compatibility notices are more informative than silent rejection or a false assertion of validity.

# Consequences

- UI and indexing interfaces should represent independent diagnostic categories, not one `valid` boolean.
- Profile-specific checks must be optional and replaceable.
- The M0 fixture corpus must test malformed YAML, skipped Markdown, unknown types/extensions, unsupported version declarations, broken links, and ambiguous references.
- Precise severity levels and machine-readable diagnostic codes remain to be established during implementation.

# References

- [Engineering Profile](../../profiles/engineering/profile.md)
- [Explorer specification](../specifications/explorer.md)
- [M0 compatibility plan](../plans/m0-compatibility.md)
- [OKF v0.3 specification](https://github.com/open-knowledge-format/open-knowledge-format/blob/main/SPEC.md)
