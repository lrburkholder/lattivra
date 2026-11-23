---
type: Decision
title: D-010 — Defer Dynamic External Profile Loading
status: stable
tags: [profiles, explorer, deferred, mvp]
---

# Context

OKF v0.3 permits producer-defined concept types and extensions without a central schema registry. Lattivra Explorer must remain useful for arbitrary OKF bundles, and the Engineering Profile is optional. Automatically discovering and executing or interpreting third-party validation definitions would add compatibility, security, and maintenance obligations before M0 establishes a reliable OKF baseline.

# Decision

**Decision ID:** D-010. **Approval:** accepted decision to defer dynamic third-party profile discovery/loading; implementation of such support is not approved for the MVP.

- Do not require an external profile registry, remote profile fetch, automatic schema loading, or execution of arbitrary validation code.
- Treat unknown artifact types as ordinary OKF concepts. Display their Markdown, native metadata, and unknown extension fields without rejecting them for lack of a profile.
- Keep generic OKF validation separate from optional known-profile checks. Lattivra's own Engineering Profile may be supported as a static, explicitly enabled optional feature.
- Do not interpret untrusted profile content as instructions or grant it authority over local files or actions.

# Rationale

Dynamic profile handling does not help prove the primary MVP requirements: multi-bundle discovery, search, rendering, provenance, references, and deterministic diagnostics. Deferral reduces scope while preserving general-purpose OKF compatibility.

# Consequences

- The Explorer can inspect third-party artifacts without applying their domain-specific constraints.
- Unknown profile-specific rules will not be validated in MVP; this limitation should be visible rather than mislabeled as a validation success.
- Future support must distinguish declarative data schemas from executable extensions and define version selection, trust, offline behavior, and failure modes.

# Revisit Trigger

Revisit after M0 and an operational MVP if multiple real external profiles demonstrate a concrete need that cannot be handled through generic OKF rendering and explicitly configured validation adapters. A later decision must define a safe discovery and loading contract before implementation.

# References

- [D-005 profile foundation](d005-profile-format.md)
- [D-009 validation policy](d009-validation-policy.md)
- [Explorer specification](../specifications/explorer.md)
- [M0 compatibility plan](../plans/m0-compatibility.md)
