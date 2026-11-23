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
2. **Optional Engineering Profile conformance:** Apply the bootstrap profile only when explicitly selected for a bundle in Explorer configuration or for a standalone validation run. A matching `type` name alone does not claim profile conformance. Within the selected scope, check the profile's three known types for required headings and optional extension-value rules; leave other types as ordinary OKF. Report profile checks as not applied outside that scope. A profile failure does not imply an OKF conformance failure. A generic Explorer must work without loading this profile, and selection requires no new frontmatter field.
3. **Reference diagnostics:** Report unresolved links, ambiguous cross-source mappings, and unsupported external resolution separately from format or profile validity. Broken links do not invalidate OKF concepts.
4. **Unsupported versions:** Report a declared OKF version that the Explorer does not fully support as a compatibility diagnostic; attempt best-effort parsing per upstream guidance rather than automatically refusing the bundle.
5. **Isolation:** Continue indexing valid concepts when other files are malformed. Retain actionable file/field/location context for diagnostics where available; do not claim invalid documents were successfully indexed as valid concepts.
6. **Configuration and access diagnostics:** Report rejected duplicate/overlapping bundle registrations and blocked filesystem access separately from document conformance. An invalid Explorer configuration or an inaccessible target does not by itself make the source bundle non-conformant.

Optional metadata follows OKF's tolerant consumer rules: treat null, empty strings, and empty lists as absent, accept single-item forms of list fields, and ignore incomplete family entries with a warning. Preserve unknown fields and out-of-vocabulary values without rejecting the bundle. An unknown `status` is excluded from current-knowledge results, and an unparseable `stale_after` is never treated as fresh. These cases must not be conflated with malformed YAML.

# Rationale

Separate diagnostic layers preserve native OKF semantics, allow third-party artifacts to remain useful, and avoid converting optional Lattivra conventions into universal requirements. Explicit compatibility notices are more informative than silent rejection or a false assertion of validity.

# Consequences

- UI and indexing interfaces should represent independent diagnostic categories, not one `valid` boolean.
- Profile-specific checks must be optional and replaceable.
- The M0 fixture corpus must test malformed YAML, skipped Markdown, unknown types/extensions, tolerant optional metadata handling, explicit profile selection, unsupported version declarations, broken links, ambiguous references, registration conflicts, and filesystem boundaries.
- Precise severity levels and machine-readable diagnostic codes remain to be established during implementation.

# References

- [Engineering Profile](../../profiles/engineering/profile.md)
- [Explorer specification](../specifications/explorer.md)
- [M0 compatibility plan](../plans/m0-compatibility.md)
- [OKF v0.3 specification](https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md)
- [Pinned contract and conformance checklist](../compatibility/okf-v0.3-conformance.md)
