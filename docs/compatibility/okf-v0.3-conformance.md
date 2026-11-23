---
type: Specification
title: M0 — Pinned OKF v0.3 Contract and Conformance Checklist
status: draft
tags: [m0, okf, compatibility, conformance]
sources:
  - id: okf-v03
    resource: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md
    title: Open Knowledge Format v0.3 specification
---

# Context

This document establishes the contract for M0 fixtures and tool evaluations under [issue #2](https://github.com/lrburkholder/lattivra/issues/2). It records expected behavior, not a claim that Lattivra or another tool has passed every check. The [fixture harness](m0-harness.md) supplies executable examples and reports their actual outcomes and remaining gaps.

## Normative baseline

| Item | Pinned value |
| --- | --- |
| Upstream repository | [open-knowledge-format/open-knowledge-format](https://github.com/open-knowledge-format/open-knowledge-format) |
| Specification | [SPEC.md at the reviewed commit][spec] |
| Declared version | `0.3` |
| Commit | `527e81aff55992be21507e97004286789126f88c` |
| `SPEC.md` Git blob | `0dc3f7aa0fc710e588ba918eb115935d41eb2943` |
| Review date | 2026-11-22 |

The commit-pinned text governs this checklist. The blob identifies that file's Git object; it is not a commit or a checksum of the entire upstream repository. A tool evaluation must record this baseline and its own revision. Updating upstream `main` does not update this contract. Change the pin and affected expectations together in a reviewed change, including any changes to normative text that retain the same declared version.

# Requirements

## Reading and recording results

Each row has a stable ID for fixture and result references. Record its fixture path, tool/revision, actual outcome, and evidence when executing it. Split rows into multiple fixture cases where they describe variants. Record optional capabilities as supported or unsupported, and unresolved cases as unresolved; neither is an automatic failure. Consult the [harness traceability report](m0-harness.md#checklist-traceability-and-limits) for executed examples, pending rows, and skips; this checklist itself defines expectations.

Keep these result dimensions separate, following [D-009](../decisions/d009-validation-policy.md):

- **Bundle conformance:** structural/frontmatter and reserved-file requirements in upstream §11.1. Producer requirements and recommendations are identified separately where they exceed that narrow definition.
- **Consumer compatibility:** whether a tool follows required reading and interpretation behavior. A consumer defect does not make its input bundle invalid.
- **Profile conformance:** only for explicitly selected Engineering Profile checks; otherwise report not applied.
- **Diagnostics:** references, version compatibility, configuration, access, and optional metadata warnings. A warning alone does not imply bundle failure.

Upstream MUST/MUST NOT rules are requirements; SHOULD rules are recommendations; MAY rules are optional. A Lattivra choice or unresolved interpretation is explicitly labelled. Do not convert recommendations, missing optional capabilities, or unresolved interpretations into universal OKF failures.

## Discovery, identity, and reserved files

| ID | Fixture / operation | Expected behavior | Basis |
| --- | --- | --- | --- |
| DISC-01 | Root and nested `.md` files with `type: Metric`; an unfamiliar nonempty string type | Discover both as concepts, including the unfamiliar type. IDs are their bundle-relative paths without `.md`. No global ID field is required. | [§2][s2], [§3.2][s3-2], [§4.1][s4-1] |
| DISC-02 | `.md` files with no frontmatter, or a mapping without `type` | Skip as non-concepts without making the bundle invalid. A validator SHOULD warn. Include an ordinary `README.md` case. | [§3.2][s3-2], [§11.1][s11-1] |
| DISC-03 | Non-`.md` file, including an image or code file | Treat as an asset, never a concept; links and path fields may target it. | [§3.2][s3-2] |
| DISC-04 | `.hidden.md` and `.hidden/concept.md` alongside a visible concept | Exclude dot-prefixed files and entire dot-prefixed subtrees from the bundle scan and conformance scope; retain the visible concept. | [§3.2][s3-2] |
| DISC-05 | A symbolic link escapes the registered root, including an indirect escape | Do not traverse or read the outside target. Lattivra reports an access diagnostic separately and continues reading valid in-root concepts. | [§3.2][s3-2]; [Explorer EXP-005](../specifications/explorer.md#sources-and-discovery), D-009 |
| RES-01 | `index.md` and `log.md` at root and in subdirectories, even with a `type` | Never index these reserved names as concepts. Invalid reserved-file structure is still a bundle-conformance issue; skipping them as concepts does not suppress it. | [§3.1][s3-1], [§11.1][s11-1] |
| RES-02 | A bundle/directory without an index or log | Accept; both are optional. Generating a directory index is an optional consumer capability. | [§8][s8], [§9][s9], [§11.2][s11-2] |
| RES-03 | Root index with bundle metadata and an extension; nested index with frontmatter | Accept the root metadata without inheriting it into concepts. Report the nested index's frontmatter as a reserved-file conformance failure within the registered bundle. Do not silently make it another bundle. | [§8][s8], [§8.1][s8-1], [§11.1][s11-1]; D-007 |
| RES-04 | Index body with headings and linked entries | Recognize the directory listing. Including linked concepts' descriptions is recommended, not required. | [§8][s8] |
| RES-05 | Regeneration of an existing root index by a candidate producer | Preserve all existing root-index frontmatter. This is a producer check; read-only Explorer does not regenerate source files. | [§8.1][s8-1] |
| RES-06 | Log with newest date first, `YYYY-MM-DD` headings and prose entries; variants with frontmatter or malformed date headings | Accept the first log; report the variants as reserved-file conformance failures. Bold action labels are optional conventions. | [§9][s9], [§11.1][s11-1] |

## Frontmatter and body

| ID | Fixture / operation | Expected behavior | Basis |
| --- | --- | --- | --- |
| FM-01 | UTF-8 concept whose first line and closing delimiter are exactly `---`, with a YAML mapping | Parse the mapping and Markdown body. A later `---` in the body does not extend the frontmatter. | [§4][s4] |
| FM-02 | Opened frontmatter with no closing delimiter, invalid YAML, or a sequence/scalar instead of a mapping | Report a frontmatter conformance failure. Lattivra continues with valid neighboring concepts and does not claim the invalid file was indexed as a valid concept. | [§4][s4], [§11.1][s11-1]; D-009 |
| FM-03 | Mapping with extension values `on`, `yes`, `true`, and quoted `"0.3"` | Under YAML 1.2 core, the first two remain strings, `true` is boolean, and `"0.3"` is a string. A YAML 1.1 parser silently producing other values fails compatibility. | [§4][s4] |
| FM-04 | Duplicate mapping keys, including nested keys | A producer violates the no-duplicates rule. Upstream permits consumer rejection; Lattivra chooses rejection with a frontmatter diagnostic (D-009). Do not call rejection mandatory for every consumer. | [§4][s4]; D-009 |
| FM-05 | `type: Reference` with no other metadata or body headings | Accept a minimal concept; missing title, provenance, verification, and profile headings do not cause OKF failure. | [§4.1][s4-1], [§4.2][s4-2], [§11.2][s11-2] |
| FM-06 | Unknown top-level keys and unknown nested keys in `sources`, `generated`, `verified`, `executor`, and `attester` | Accept without unknown-key rejection. Upstream requires modifying producers to preserve unknown keys; Lattivra retains raw metadata without rewriting source files. The `x-` naming pattern is recommended, not required. | [§4.1][s4-1]; D-009 |
| FM-07 | CommonMark links, a GFM table, and source-labelled footnotes; arbitrary body headings | Recognize the specified Markdown forms; no general body heading is required. The Engineering Profile's headings are a separate check. | [§4.2][s4-2] |
| FM-08 | Candidate producer edits one field; other values look numeric/boolean or use custom YAML tags | Quoting ambiguous values, avoiding custom tags, and avoiding reserialization of unchanged values are producer recommendations. Do not turn them into unconditional bundle failures. Custom-tag consumption remains unresolved (U-06). | [§4][s4] |

## Optional metadata and provenance

| ID | Fixture / operation | Expected behavior | Basis |
| --- | --- | --- | --- |
| META-01 | Each optional field set to null, `""`, or `[]`, versus omitted | Consume those values as absent without bundle failure. Preserve the original source file. This rule does not resolve malformed required `type` values (U-01). | [§11.2][s11-2] |
| META-02 | Singleton `tags`, `sources`, `verified`, or `parameters` instead of a list | Consume one item as a one-element list. `tags: "alpha,beta"` is one tag, never two. | [§11.2][s11-2] |
| META-03 | Source missing `resource`; `generated` missing `by`; verification missing `by` or `at`; parameter missing `name` or `type` | Ignore the incomplete family entry and SHOULD warn, without bundle failure; retain valid sibling entries. Malformed field shapes beyond these explicit rules are U-06. | [§5.1][s5-1], [§5.2][s5-2], [§10.2][s10-2], [§11.2][s11-2] |
| META-04 | Source with URL, bundle path, or a population descriptor as `resource` | Retain all three forms. Resolve actual paths using §6; do not force a scope description into a broken filesystem link. Classification ambiguity is U-03. | [§5.1][s5-1], [§6.2][s6-2] |
| META-05 | Two sources reordered while footnote labels still match their `id` keys | Attribute a claim using its source ID, independently of list order or footnote display text. Do not use a positional join. | [§4.2][s4-2], [§5.1][s5-1] |
| META-06 | Source author, usage count, modification time, a shared usage window, and an entry-specific window | Retain the credibility signals; the entry's window overrides the shared one for that entry. Do not invent a portable credibility score or treat source usage as verification. | [§5.1][s5-1] |
| META-07 | Quoted RFC 3339 offset date-time and date-only values in timestamp fields; native timestamp/date values if surfaced by the parser | Accept equivalent timestamp representations. A date-only value means midnight UTC; a date-time without an offset is not a valid timestamp. Test invalid staleness with STATE-06; generation-time ambiguity is U-02. | [§5][s5] |
| META-08 | Native Markdown and a projection with source URI and `sources[].x-lattivra-revision` | Neither requires a global concept ID. Lattivra preserves the opaque revision exactly and does not elevate the projection or index over declared upstream authority. This extension's meaning is local profile policy. | [§4.1][s4-1], [§5.1][s5-1]; [profile](../../profiles/engineering/profile.md#provenance-and-projections) |

## Links, path fields, and graph behavior

Use a concept at `a/source.md`, a neighboring concept at `a/target.md`, and another at `target.md` to distinguish directory-relative from root-relative resolution.

| ID | Fixture / operation | Expected behavior | Basis |
| --- | --- | --- | --- |
| PATH-01 | Body links to `target.md`, `./target.md`, and `/target.md` from `a/source.md` | The first two resolve to `a/target.md`; the third resolves to `target.md` under the bundle root. All forms are accepted. | [§6][s6], [§6.1][s6-1] |
| PATH-02 | The same path variants in `resource`, `sources[].resource`, `computation`, `executor.resource`, `attester.resource`, and `superseded_by` | Apply the same resolution rules to each field, excluding source scope descriptors. `license` may also be a bundle-relative license-file path per §8.1. | [§6.2][s6-2], [§8.1][s8-1] |
| PATH-03 | An `https:` or other scheme-bearing URI; `../../outside.md` escaping the root | Keep scheme-bearing values external. Never read an escaped local target. Lattivra reports blocked access separately; the reference does not invalidate its origin concept. | [§6][s6]; D-009 |
| PATH-04 | `my%20concept.md#details` and a target with a different case | Decode the URI path for resolution and disregard the fragment when identifying the target concept. Match paths case-sensitively even on a case-insensitive host. Producers must encode spaces/reserved characters and SHOULD avoid names differing only by case. | [§6][s6], [§6.1][s6-1] |
| PATH-05 | Inline and reference-style Markdown links, plus `[[wikilinks]]` | The two standard forms can create concept relationships; wikilinks are not OKF links. | [§6.1][s6-1] |
| PATH-06 | A concept link, an asset link/image, a directory link, a non-concept Markdown link, and a broken link | Only the concept target creates a concept edge. The other targets remain valid references; broken links do not invalidate concepts or bundles. | [§3.2][s3-2], [§6.1][s6-1], [§11.2][s11-2] |
| PATH-07 | A body link and a path field that each resolve to a concept | Both create directed graph edges. Neither imposes a typed relationship or parent/child hierarchy; directory nesting supplies hierarchy. | [§6.1][s6-1], [§6.4][s6-4] |
| PATH-08 | Concept outside `references/`, and a bundle with no `references/` directory | Accept both; the directory is a naming convention, not a special discovery or validity rule. | [§6.3][s6-3] |

## Trust and lifecycle

Use fixed timestamps and an explicit evaluation clock so outcomes do not depend on the CI run date.

| ID | Fixture / operation | Expected behavior | Basis |
| --- | --- | --- | --- |
| STATE-01 | No `generated` or `verified`; valid verification with no `generated` | The first is consumable and unverified. In the second, the valid verification is current. Missing optional families never cause rejection. | [§5.3][s5-3], [§11.2][s11-2] |
| STATE-02 | Generation at T; valid verification before T, at T, and after T | Ignore earlier events for trust tier; equality and later events qualify. Historical events may still be displayed. A stale human review cannot override a current machine event. | [§5.3][s5-3] |
| STATE-03 | Current events from an agent/tool, `process:`, `team:`, an unfamiliar scheme, or `human:` | Non-human events alone yield machine-confirmed; a current `human:` event yields human-reviewed; no current events yields unverified. Accept unknown actor schemes as non-human. Trust is advisory, never access authorization. | [§5.3][s5-3], [§7][s7] |
| STATE-04 | Missing status, each known status, and an unfamiliar status such as `accepted` | Missing status means stable. Preserve unfamiliar values, optionally warn, and exclude them from current-knowledge filters. Deprecated concepts remain available for links/history; do not reinterpret approval as OKF status. | [§5.4][s5-4], [§11.2][s11-2] |
| STATE-05 | Deprecated concept with a resolvable or broken `superseded_by`; same field on a stable concept | Replacement meaning applies only to deprecated concepts. Current-knowledge consumers SHOULD follow a resolvable replacement; a broken replacement produces a reference diagnostic. Cycle handling is U-07. | [§5.4][s5-4], [§6.2][s6-2] |
| STATE-06 | Evaluation immediately before, at, and after `stale_after`; malformed value; empty value | Valid threshold is stale at equality and afterward. An unparseable value is never fresh and SHOULD be shown as malformed. Empty means absent. Absence supplies no review deadline; do not invent one. | [§5.5][s5-5], [§11.2][s11-2] |
| STATE-07 | Different generation times with the same staleness deadline | Staleness SHOULD depend only on the deadline, not generation or ingestion time. Stale content needs review; it is not thereby false. | [§5.2][s5-2], [§5.5][s5-5], [§11.2][s11-2] |

## Version handling and optional legacy behavior

| ID | Fixture / operation | Expected behavior | Basis |
| --- | --- | --- | --- |
| VER-01 | Root index declares `okf_version: "0.3"`; another bundle has no version or index | Read the declared bundle version from root metadata. Missing version/index does not cause rejection. A nested index never overrides the registered bundle version. | [§8.1][s8-1], [§11.2][s11-2], [§12][s12]; D-007 |
| VER-02 | Unknown declared version with otherwise readable concepts | SHOULD attempt best-effort reading rather than refusal. Lattivra emits a compatibility diagnostic and does not claim full support for the unknown version. | [§12][s12]; D-009 |
| VER-03 | A bare path field fails directory-relative resolution but exists at root, with version 0.2, earlier, or absent | Root fallback is optional. Record whether each tool supports it; lack of support is not a v0.3 conformance failure. Never prefer fallback over an existing directory-relative target. | [§6.2][s6-2], [§12.1][s12-1] |
| VER-04 | The VER-03 case declaring 0.3; a body link instead of a path field | Do not apply the legacy root fallback to declared v0.3, or broaden it to ordinary body links. An unresolved target remains a reference diagnostic. | [§6][s6], [§6.2][s6-2], [§12.1][s12-1] |
| VER-05 | Legacy `timestamp` without `generated`, or legacy body `Citations`, in an old/unversioned bundle | Recognizing these v0.1 forms is optional. Record support separately; never require legacy fields for v0.3. | [§12.1][s12-1], [Appendix B][app-b] |

## Attested computation metadata (static checks only)

Explorer remains read-only and does not run executors, attesters, or embedded code. These cases check interpretation without implementing an execution protocol. Upstream §10.5 describes an informative runtime flow; it is not a requirement to add execution to Explorer.

| ID | Fixture / operation | Expected behavior | Basis |
| --- | --- | --- | --- |
| ATT-01 | `type: Attested Computation` with/without `runtime` and `attester` | Recognize the type; never label a value attested if runtime or attester is missing. Missing type-specific runtime is a producer-contract issue; its classification under narrow §11.1 is U-08. Presence of both fields alone is no evidence of a successful attestation. | [§10.2][s10-2], [§11.2][s11-2] |
| ATT-02 | Valid parameter entry without `required`; incomplete entry | Default the former to optional (`false`); ignore the incomplete entry and SHOULD warn. Runtime-specific parameter types need not belong to a global vocabulary. | [§10.2][s10-2], [§11.2][s11-2] |
| ATT-03 | `computation` path plus an inline block; missing target file | The path takes precedence. A missing file makes the concept not attestable, even if an inline block exists; report the unresolved reference separately. | [§10.3][s10-3] |
| ATT-04 | No computation path; an ATX `Computation` heading with two fenced blocks, followed by a same/higher-level heading | Locate the first fenced block within that section at any ATX level. Do not select a later section's block. Exactly one block is recommended. With no block in the section, the concept is not attestable. | [§10.3][s10-3] |
| ATT-05 | A human-reviewed definition without per-run evidence | Verification of a definition does not attest any run. Neither source metadata nor verification authorizes executing imported content. | [§10.6][s10-6]; [foundation](../specifications/foundation.md#requirements) |

## Lattivra-specific checks

These expectations are local requirements. Failure is not automatically an OKF bundle-conformance failure.

| ID | Fixture / operation | Expected behavior | Basis |
| --- | --- | --- | --- |
| LAT-01 | Two registered bundles each contain `decisions/example.md` | Keep their native IDs equal but their Explorer identities distinct through persistent registration identity. Provenance equality does not merge concepts. | [D-006](../decisions/d006-cross-source-identity.md) |
| LAT-02 | An unregistered ordinary subdirectory contains `index.md` and concepts | Scan it within the registered containing bundle. Do not discover another independent bundle or change root-relative paths automatically. | [D-007](../decisions/d007-bundle-discovery.md); see U-04 |
| LAT-03 | Duplicate or ancestor/descendant roots, including filesystem aliases | Reject the proposed registration, name both roots in a configuration diagnostic, and retain accepted registrations. Do not mark source documents invalid. | D-007, D-009 |
| LAT-04 | Generic `Decision` without profile headings, with profile checks off then explicitly selected | OKF remains valid in both runs. Report profile not applied in the first; missing profile headings only as profile failures in the second. Unknown types remain ordinary OKF in a selected bundle. | [profile](../../profiles/engineering/profile.md#initial-type-names-and-body-conventions), D-009 |
| LAT-05 | External URI with zero, one, or multiple explicit cross-source matches | Resolve only the unique explicit mapping. Retain unmapped external references and diagnose ambiguity; do not guess from filenames or source revisions. | D-006, D-009 |
| LAT-06 | Discovery, indexing, refresh, rebuild, and navigation over fixtures with malformed neighbors | Valid concepts remain usable, and input bytes remain unchanged. Record parsing, access, and reference diagnostics independently; malformed neighbors must not be silently counted as valid concepts. | [M0 plan](../plans/m0-compatibility.md#verification), D-009 |

## Unresolved interpretations and explicit limits

These cases need investigation or a documented local policy before executable expectations become merge requirements. Upstream wording is not silently strengthened here.

| ID | Uncertainty | Treatment for M0 |
| --- | --- | --- |
| U-01 | §3.2 requires nonempty `type`; §4.1 describes a short string. Null, empty string, whitespace-only, boolean, numeric, mapping, and list values are not fully classified by §11.1. | Include separate cases. A missing type is definitely skipped (DISC-02); do not invent string coercion or a universal conformance verdict for malformed types. Record discovery and producer diagnostics separately pending policy. |
| U-02 | `generated.by` is marked REQUIRED but `generated.at` is not. §5.3 does not say how to compare verification times when `generated` exists without a usable `at`. Invalid verification timestamps are similarly underspecified. | Preserve values, flag the ambiguity, and do not claim human-reviewed or current-event evidence from an undefined comparison. Any conservative fallback must be labelled local policy. |
| U-03 | `sources[].resource` permits both relative paths and unrestricted population descriptions, without a discriminator. | Use unambiguous examples for normative path tests. Record classification behavior for ambiguous strings; a producer convention or heuristic is not an upstream rule. |
| U-04 | §2 allows a root index to identify a bundle in a larger repository but supplies no automatic recursive root-discovery algorithm. | D-007 explicitly selects roots; a nested index alone never splits one. Distinguish a nested-index structure issue from an overlapping-registration issue. |
| U-05 | §3.2 prohibits escaping symlinks but does not define in-root symlink traversal, cycle handling, alias deduplication, or all platform-specific junction behavior. | Test escapes as required; record in-root support and limitations separately. No candidate may read outside the registered root. Explorer's alias boundary is additional local policy. |
| U-06 | Arbitrary wrong-shaped optional values, YAML custom tags/merge-key behavior, byte-order marks, and malformed URI references are not exhaustively specified. | Keep explicit YAML 1.2 mapping, absence, singleton, and incomplete-entry tests separate. Record unsupported syntax and diagnostics without claiming broader upstream rejection rules. |
| U-07 | `superseded_by` recommends following replacements but does not define cycles or maximum chain length. | Add cycle/missing-target cases and record the tool's bounded behavior. Do not make graph incompleteness a bundle failure. |
| U-08 | §10.2 requires runtime for Attested Computation producers, while §11.1 defines bundle conformance structurally and §11.2 tolerates incomplete optional families. | Record the missing runtime as a type-specific producer-contract diagnostic and not-attested state. Resolve any stronger bundle-failure claim explicitly before using it as a gate. |

## Automation

The [fixture harness and workflow](m0-harness.md) map executable examples to these IDs and record expected versus actual results. Checks run on pull requests and pushes to `main`, with a fixed evaluation clock and this exact upstream revision. Reports separate format, selected-profile, and diagnostic outcomes, with consumer coverage limits recorded explicitly. A deliberately broken fixture producing its expected diagnostic is a successful test of that behavior.

Capability gaps and unresolved cases remain visible in the checklist traceability report; baseline upgrades require review instead of silently fetching upstream `main`. Passing examples do not establish complete consumer conformance.

# Acceptance Criteria

1. The normative source is linked at an immutable commit and its `SPEC.md` blob matches the previously reviewed blob.
2. Every defined checklist row gives fixture inputs/operations, an observable expected result, and an upstream section or local-policy reference.
3. Discovery, reserved files, YAML 1.2, unknown types/extensions, paths, provenance, trust, lifecycle, and version fallbacks are covered.
4. Unresolved interpretations are named; optional capabilities and recommendations are distinguishable from requirements.
5. No global concept-ID requirement or automatic nested-bundle discovery is introduced.
6. OKF conformance, consumer compatibility, selected profile conformance, and diagnostics remain independent, consistent with D-009.

[spec]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md
[s2]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#2-terminology
[s3-1]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#31-reserved-filenames
[s3-2]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#32-concepts-assets-and-other-files
[s4]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#4-concept-documents
[s4-1]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#41-frontmatter
[s4-2]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#42-body
[s5]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#5-provenance-trust-and-lifecycle
[s5-1]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#51-provenance-sources
[s5-2]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#52-trust-generated-and-verified
[s5-3]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#53-trust-tiers
[s5-4]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#54-lifecycle-status-and-superseded_by
[s5-5]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#55-lifecycle-stale_after
[s6]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#6-links-and-paths
[s6-1]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#61-links-between-concepts
[s6-2]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#62-path-fields
[s6-3]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#63-the-references-convention
[s6-4]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#64-the-bundle-graph
[s7]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#7-actor-convention
[s8]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#8-index-files
[s8-1]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#81-bundle-metadata
[s9]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#9-log-files
[s10-2]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#102-contract-fields
[s10-3]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#103-the-computation
[s10-6]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#106-verification-and-attestation
[s11-1]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#111-bundle-conformance
[s11-2]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#112-consumer-rules
[s12]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#12-versioning
[s12-1]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#121-bundles-from-earlier-versions
[app-b]: https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md#appendix-b-changes-from-v01-to-v02
