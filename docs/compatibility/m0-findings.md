---
type: Evaluation
title: M0 findings — OKF compatibility and Battalion interoperability
status: stable
tags: [m0, okf, engineering-profile, battalion]
---

# M0 findings

The read-only harness recovered nine concepts from two independently registered OKF v0.3 roots, including two decisions with the same native ID. All expected fixture outcomes matched. The Engineering Profile can be used directly in Markdown and checked offline. The next milestone can exercise that file contract with Battalion while both Explorer decisions remain deferred. [M0 exit criteria](../plans/m0-compatibility.md#exit-criteria)

## Results against the fixture inventory

| Probe | Observed outcome |
| --- | --- |
| Discovery and source integrity | Alpha yielded seven concepts and Beta two. A third root declaring version 99 yielded one concept and a compatibility warning. All 24 SHA-256 entries (23 fixture files and the inventory) matched before and after the scan. Duplicate and overlapping registration attempts each produced a configuration diagnostic. |
| Identity and navigation | Both roots supplied `decisions/shared`. Alpha's root-relative link resolved to Alpha's decision. Its uniquely mapped external URI resolved to Beta's decision. The ambiguous URI and `missing.md` produced separate reference diagnostics and neither contributed a backlink. |
| Format and recovery | Alpha failed structural conformance on invalid YAML, a duplicate key, and sequence-valued frontmatter. Its valid neighbors, including an unfamiliar type with nested extension data, remained readable. Beta passed the structural checks. |
| Optional profile | Alpha's native and projected specifications, profiled decision, and implementation plan passed the selected checks. Its generic Decision produced four missing-heading diagnostics. With the profile unselected the same generic document remains valid OKF and its profile result is `not_applied`. |
| Provenance | The reader preserved the projected source URI, generator, and Alpha's opaque `synthetic-revision-007` on its source entry. Beta's projection retained its URI with the revision absent. Both projections were read offline. |

The fixture inventory specifies expected results per file. The test suite also moves a bundle outside the manifest directory and verifies that changes to its source bytes are detected. The report records actual diagnostics, resolved targets, the evaluation clock, and source hashes. [Fixture inventory](../../tests/fixtures/corpus.json) · [Executable assertions](../../tests/test_m0.py)

## Reproduce the baseline

Use Lattivra commit `d6eada927e08926415463d79dc595c59e0fdd811` for the reader, fixtures, and Catalog runner. The normative input is OKF v0.3 commit `527e81aff55992be21507e97004286789126f88c`, with `SPEC.md` blob `0dc3f7aa0fc710e588ba918eb115935d41eb2943`. The fixture clock is `2026-11-22T00:00:00Z`. [Tested Lattivra tree](https://github.com/lrburkholder/lattivra/tree/d6eada927e08926415463d79dc595c59e0fdd811) · [Pinned OKF specification](https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md)

From that checkout on Windows, using Python 3.14.6, run

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-m0.txt
.\.venv\Scripts\python.exe -m m0_harness tests/fixtures/corpus.json --output artifacts/conformance.json
.\.venv\Scripts\python.exe -m pytest -q --contract-report=artifacts/checklist-coverage.json
```

The fixture command exited 0 with an empty `expectation_failures` list and `sources_unchanged` true. The Windows suite passed 86 tests, including the junction boundary check. One symbolic-link test skipped because the account lacked symlink privileges. The same commands run with `.venv/bin/python` on Linux. [Pinned packages](../../requirements-m0.txt) · [Harness and CI guide](m0-harness.md)

## Compatibility limits

Eight checklist rows still lack dedicated assertions. They cover directory listings and index regeneration (RES-04/05), Markdown dialect and serialization (FM-07/08), claim attribution and credibility windows (META-05/06), following replacement chains (STATE-05), and legacy metadata fallbacks (VER-05). A passing example exercises only the behavior asserted.

Eight interpretations also remain open. They concern malformed `type` values, missing trust timestamps, path versus prose source descriptors, nested bundle discovery, filesystem aliases, optional-value and YAML edge cases, replacement cycles, and missing computation runtimes (U-01 through U-08). For example, the reader skips in-root aliases and reports custom YAML tags as compatibility limits. The checklist distinguishes these local choices from the pinned contract. [Checklist and unresolved interpretations](okf-v0.3-conformance.md#unresolved-interpretations-and-explicit-limits) · [Coverage limits](m0-harness.md#checklist-traceability-and-limits)

## Indexing and UI decisions

Open Knowledge Catalog (OKC) v0.1.0 read the fixture files without changing them and exposed structured provenance. In a combined Windows index, search could return both shared decisions but path lookup could retrieve only one. After an edit the old term still matched, and after deletion a surviving link still reported the target as present. The closeout rerun confirmed that refreshed and rebuilt results differed for documents, metadata, links, validation diagnostics, and search. Tags and low-level scan errors matched.

The tested Windows release corresponds to upstream commit `83b4625d847d4f0be219a166a9308034245ba274`. The evaluation records the release asset hash, download and runner commands, and per-operation results. D-004 recommends against adopting this release as-is. Comparing adapter repairs with an independent indexer can wait until a concrete search use case warrants the work. D-003 keeps standalone UI work deferred until Battalion can support building it and the maintainer elects to resume. [Catalog evaluation and reproduction](open-knowledge-catalog.md) · [D-004](../decisions/d004-indexing-engine.md) · [D-003](../decisions/d003-explorer-platform.md)

## M1 — Exchange one engineering artifact with Battalion

The smallest follow-on is one file-based interoperability test. Use the existing projected Specification as the example. M0 tested synthetic Battalion-style records. An artifact produced or consumed by Battalion itself is the evidence M1 still needs.

1. **Produce.** Export one synthetic Battalion requirement into a test bundle as a UTF-8 OKF Specification with the profile's Context, Requirements, and Acceptance Criteria headings. Carry the upstream resource URI and actual generator in the projection. Preserve an available exact revision on its source entry and leave it absent when unavailable. The upstream requirement remains authoritative. Native Markdown can be authored directly using the same headings. [Profile conventions](../../profiles/engineering/profile.md) · [Versioned example](../../tests/fixtures/.bundles/alpha/specifications/projected.md) · [Unversioned example](../../tests/fixtures/.bundles/beta/specifications/unversioned.md)
2. **Consume.** Read the exported file from its registered bundle in an independent process. Compare the bundle-relative concept ID, body, source entry, generation metadata, and unknown fields with the producer's expected values. Read ordinary OKF with profile checks off, then select the Engineering Profile and check the headings. Keep workflow approval in the artifact body or the upstream system, with OKF `status` reserved for lifecycle.
3. **Verify.** Deliver the synthetic input, exported bundle, expected values, and a repeatable command. Acceptance requires matching source hashes around consumption and separate format, profile, and reference results. Keep Battalion-specific export code on the producer side so another Markdown tool can use the profile and run the same checks independently. The experiment needs only files, explicit registration, and the existing reader.
