---
type: Specification
title: Lattivra Engineering Profile — bootstrap v0.1 draft
description: Minimal Markdown-first conventions for three engineering artifact types based on OKF v0.3.
status: draft
tags: [engineering-profile, interoperability, specification]
sources:
  - id: okf-v03
    resource: https://github.com/open-knowledge-format/open-knowledge-format/blob/main/SPEC.md
    title: Open Knowledge Format v0.3 specification
---

# Context

Lattivra needs interoperable engineering documentation without creating a competing format. This bootstrap profile is intentionally minimal; **it is not a published stable standard**. All conforming documents are ordinary OKF v0.3 Markdown concepts. The profile must work independently of Lattivra Explorer and Battalion.

# Requirements

## Base format

- A profiled artifact MUST be an OKF v0.3 concept: a UTF-8 `.md` file beginning with YAML frontmatter that contains a nonempty `type`.
- Use native OKF frontmatter when applicable: `title`, `description`, `resource`, `tags`, `sources`, `generated`, `verified`, `status`, `superseded_by`, and `stale_after`.
- Producers MUST NOT use OKF `status` for approval state or workflow state. Its vocabulary is `draft`, `stable`, `deprecated` and absence means `stable`. A decision may be accepted in the body while the document's OKF `status` is `draft`.
- Profile-specific sections MUST be Markdown headings and readable without a specialized renderer.
- Consumers must preserve unknown frontmatter keys according to OKF; support for profile-specific interpretation is optional.

## Initial type names and body conventions

The following **exact, case-sensitive** `type` strings are defined by this bootstrap profile. Headings shown are required for **profile conformance**, not for basic OKF conformance. Heading order is recommended but not required. Heading text is case-sensitive in the bootstrap checker, if implemented.

| `type` | Required level-1 or level-2 headings | Intended content |
| --- | --- | --- |
| `Specification` | Context, Requirements, Acceptance Criteria | Expected behavior, boundaries, measurable acceptance |
| `Decision` | Context, Decision, Rationale, Consequences | Choice and justification |
| `Implementation Plan` | Objective, Tasks, Verification | Work packages and how results will be checked |

A specification MAY add Non-Goals and Open Questions. A decision SHOULD state its decision ID and approval status in the body. A plan SHOULD distinguish dependencies and exit criteria. No universal structured requirement IDs, approval workflow, or task schema is defined in v0.1.

## Provenance and projections

- Authoritative Markdown artifacts need no external authoritative-source declaration.
- A producer MAY publish a Markdown projection of another authoritative record. It SHOULD identify the underlying source in a `sources` entry with `resource` and SHOULD pin an exact source revision where one exists.
- When an exact revision cannot be expressed by an immutable source URI, a `sources` entry MAY carry `x-lattivra-revision: "<opaque revision>"`.
- The extension MUST be a nonempty string, scoped to the source entry containing it. Its interpretation belongs to the producer; it is not a checksum, content-verification guarantee, cross-bundle artifact ID, or authorization.
- The optional source-entry `id: authoritative-source` MAY identify the primary source of a projection; this `id` is a profile convention, not an OKF-defined source role. A producer MUST NOT declare competing primary authoritative sources in one projection.
- Use OKF `generated` and `verified` accurately. Do not invent actors, verification events, or timestamps.

## Links, identity, and lifecycle

- Concept identity remains the file path relative to its OKF bundle, excluding `.md`.
- Links follow OKF v0.3 path and URI resolution rules. The profile introduces no custom `lattivra:` URI scheme.
- Cross-bundle resolution is a consumer capability and is not required for profile conformance.
- OKF `superseded_by` has its normal meaning only with `status: deprecated`; application-specific revision and approval flows are not imported into the profile.

## Scope exclusions

No required LinkML, RDF, SHACL, custom JSON Schema, graph database, approval engine, or Battalion runtime fields. Evidence, review findings, and engineering knowledge may use ordinary OKF until evidence shows they need dedicated profile types.

# Acceptance Criteria

1. A `Specification`, `Decision`, and `Implementation Plan` can each be authored and read as plain `.md` files.
2. Each example meets OKF v0.3 concept syntax and has the profile-required headings.
3. An ordinary OKF consumer can read these artifacts without understanding the profile.
4. A projected source can declare an optional exact revision without pretending that this proves provenance or content validity.
5. The profile can be validated independently of any Battalion implementation.

# Open Questions

- Should required headings remain normative when a formal validator is introduced?
- Should a later profile introduce typed evidence relationships? Only after concrete interoperability tests.

# References

- [OKF v0.3](https://github.com/open-knowledge-format/open-knowledge-format/blob/main/SPEC.md)
- [D-005 profile decision](../../docs/decisions/d005-profile-format.md)
- [D-008 types decision](../../docs/decisions/d008-initial-types.md)
