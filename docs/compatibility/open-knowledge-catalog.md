---
type: Evaluation
title: Open Knowledge Catalog v0.1.0 against the M0 fixtures
status: stable
tags: [m0, indexing, compatibility]
---

# Finding

Explorer is deferred, including backend selection. The Windows release of OKC v0.1.0 assigned both fixture decisions the same lookup path, so opening a search hit could retrieve the other bundle's document. Edits left stale text searchable, and deletion left a surviving link marked valid until a clean rebuild. These findings are recorded for use if Explorer resumes. [Issue #5](https://github.com/lrburkholder/lattivra/issues/5#issuecomment-7107109904)

## Evidence and reproduction

Tested on Windows 11 x64 (build 26300) with Python 3.14.6, using the official Windows binary from tag `v0.1.0`, commit `83b4625d847d4f0be219a166a9308034245ba274`. Lattivra fixture revision was `6dfcee2f0238631f44c6327db09d2f4d9c0cdcc6`. All three bundles matched the independent M0 oracle before comparison. [Release assets](https://github.com/guifelix/Open-Knowledge-Catalog/releases/tag/v0.1.0) · [Pinned source](https://github.com/guifelix/Open-Knowledge-Catalog/tree/83b4625d847d4f0be219a166a9308034245ba274) · [Fixture expectations](../../tests/fixtures/corpus.json)

From the Lattivra repository root with Python and the GitHub CLI available in PowerShell:

```powershell
gh release download v0.1.0 --repo guifelix/Open-Knowledge-Catalog --pattern okc-x86_64-pc-windows-msvc.exe --dir artifacts/okc-v0.1.0
python experiments/okc/evaluate.py artifacts/okc-v0.1.0/okc-x86_64-pc-windows-msvc.exe
```

The runner uses only the Python standard library and checks the Windows asset's SHA-256 before launching it (`e9910ba8b53dbd336f7d6fa55efb9d7e3902fde0e97e62a5f9121572942bc76d`). After download the experiment runs offline. To reproduce the independent expected results, use the [M0 harness commands](m0-harness.md). For a source build, check out the commit above and run `cargo build --locked --release` with Rust 1.95 or newer and a native toolchain for bundled SQLite. The Windows observations below are specific to the release binary. [Pinned build manifest](https://github.com/guifelix/Open-Knowledge-Catalog/blob/83b4625d847d4f0be219a166a9308034245ba274/Cargo.toml)

Each run prints its new directory under `artifacts/.okc-run-*`. It contains the exact TOML configs, input hashes, command arguments, exit codes and output (`*.commands.json`), plus snapshots of stored document values, links, diagnostics and actual CLI search matches. The runner uses separate copies of the registered roots and hashes every source file around every OKC command. Only test setup writes to those copies. SQLite is inspected read-only to see which metadata and edges survived when CLI results disagree. An exit code of zero from the runner means the experiment completed. Individual comparison results are in `equivalence.json`. [Evaluation runner](../../experiments/okc/evaluate.py)

## Results against the fixture oracle

| Explorer requirement and expected behavior | Observed in v0.1.0 | Consequence for reuse |
| --- | --- | --- |
| EXP-001–003, 011–012. Search enabled roots and retrieve each hit by bundle and native path. | The combined scan visited 22 Markdown files and stored 19 document rows. The three root indexes collapsed to one row and the two decisions collapsed to one. A type-filtered search returned both decision bodies under the same path. A metadata query returned only Beta and the generic Decision. Separate Alpha and Beta databases retrieved their respective titles. | One database per registration can isolate lookup. Explorer would have to persist registration IDs, select enabled databases, merge searches, and route each hit back to its source. |
| D-007. Reject duplicate and overlapping registrations while keeping the original roots. | Adding beta twice completed successfully and visited 25 files. Adding alpha's nested directory as another root also succeeded and visited 24. With ordinary registration, the nested concept remained under alpha. | Validate resolved roots in the registration layer before indexing. |
| EXP-004–006. Preserve sources, exclude dot paths and distinguish concepts from supporting files. | All 23 baseline file hashes matched around each operation, as did hashes after explicit fixture edits. Alpha's hidden file produced a YAML error and its hidden directory yielded a typed document. README, untyped Markdown, logs and directory indexes had document rows. The untyped mapping also produced a missing-type error. | Source immutability passed. Explorer needs discovery and concept filtering. The run explicitly disabled symlink following. OS permission errors, escaping symlinks and Windows junctions remain unverified for OKC. |
| EXP-007, 010, 018, 020. Read valid neighbors and distinguish format failures. | Specification, Decision, Implementation Plan and unfamiliar types remained readable. Malformed YAML and the top-level sequence produced file-specific errors in validation. The scan summary still reported zero parse failures. The duplicate-key fixture parsed successfully as `Metric`, its second type. Beta's valid root index drew an error for its title. | Preserve the file-level errors but use the pinned contract to classify conformance. Neither the scan counter nor the validator is a sufficient verdict. |
| EXP-007, 019. Preserve provenance and unknown fields. | Alpha retained its opaque `synthetic-revision-007` under the correct source entry. Beta retained its source URI with the revision absent. Native generation and verification objects survived, as did nested extensions in `unknown.md`, including the distinction between string `yes` and boolean `true`. | Structured retrieval can supply raw fields. Explorer must interpret lifecycle, provenance and verification. |
| Optional metadata, singleton lists and compatibility warnings. | Native scalar `tags: "alpha,beta"` produced no tags. In separate probes, stored null became an empty string, empty strings and lists remained present, and an incomplete source entry was retained. Unknown status and invalid staleness produced no warnings. The version-99 bundle remained readable with no version diagnostic. | Add normalization, version warnings and current/freshness rules before exposing filters or trust state. |
| EXP-013–015. Resolve relative, root and reference-style links and show backlinks. | In alpha alone, the native specification yielded the correct target strings and fragment, but existing nested targets were flagged missing. On Windows the stored document path used backslashes while link targets used forward slashes. Backlinks to the stored decision path were empty. The genuinely missing link was also flagged. Root-level links between probe documents did resolve. | Canonicalize native paths at ingestion and lookup. The root-level control also exposed an independent backlink display defect, detailed below. |
| EXP-013, 015–016. Resolve metadata paths, assets and explicit URI mappings. | The unknown type retained `sources`, `executor` and `attester` as metadata but yielded zero outgoing links. The projection's source URI also yielded no edge. The native document's unique and ambiguous Markdown URIs both remained external. The release config has no registration-to-URI mapping input. | Extract path-bearing fields and implement unique, ambiguous and unresolved mapping outcomes using bundle-qualified destinations. |
| EXP-021–022. Locate the original artifact and apply only selected profile checks. | The CLI returned a relative file path, body and metadata. In a combined index the path alone could identify either decision. Alpha's generic Decision was readable and validation emitted no missing-heading diagnostics. OKC exposes no Engineering Profile selection. | Resolve original files through the registration. Run selected profile checks separately and preserve the unselected state. |
| EXP-017–019. Present Markdown, metadata and provenance. | The CLI returned Markdown and structured metadata separately. Browser rendering, safe HTML handling and UI trust presentation were outside this backend run. | These remain Explorer responsibilities. |

## Refresh and clean rebuild (EXP-008–009, 014–015)

The combined database was rescanned after each setup change. The observer remained unchanged throughout. Using root-level links isolated refresh behavior from the Windows nested-path problem.

| Operation | Expected | Observed |
| --- | --- | --- |
| Add `probe.md` with a unique term and a link to `generic.md`. Add `observer.md` linking to the probe. | The term finds the probe, both links resolve, and backlinks identify the referring document. | The new term and both forward edges were correct. The CLI printed `generic.md` as its own backlink. The stored edge correctly identified `probe.md` as the referrer. |
| Edit the probe's title, term and link destination. | Only the new term matches. The backlink moves from `generic.md` to `unknown.md`. | The title and stored edge changed, and the old edge disappeared. Both old and new terms still returned the probe. The backlink CLI again printed the destination as the referrer. |
| Delete the probe, retaining the observer. | Remove the document, both terms and its outgoing edge. Mark the observer's link unresolved. | The row, search hits and outgoing edge disappeared. The observer still returned `probe.md` with `exists: true`. |
| Rebuild into an empty database with the same three roots, order and source bytes. | Equivalent documents, metadata, references, diagnostics and search matches. | Both indexes held 20 document rows. Refresh retained Alpha's shared decision, 14 link rows and 19 validation issues. Rebuild retained Beta's decision, 12 link rows and 17 issues. Rebuild correctly flagged the observer's link. The `decision` query returned 15 hits after refresh versus 7 after rebuild. Only tags and low-level scan errors matched across the compared dimensions. |

## Adaptation cost and license

Per-bundle databases solve the observed name collision in isolation. They still leave Windows link resolution, field-derived references, stale search entries, inbound-link invalidation and backlink presentation to fix. Full rebuilds can repair stale entries at the cost of incremental refresh. A combined rebuild still loses one decision. The missing validation and profile rules would also require an independent reader or upstream changes. Together those changes cover most of the backend that Explorer needs.

The release exposes human-readable search and navigation output, JSON validation and a private SQLite schema. Depending on that schema for a product adapter would require tracking upstream migrations. The experiment uses it only for observation. Any reevaluation of a newer release should rerun the same fixture, edit and deletion sequence on each supported platform.

OKC is MIT-licensed. Distribution of copies or substantial portions requires retaining the upstream copyright and permission notice. This experiment downloads the upstream binary separately. [Pinned license](https://github.com/guifelix/Open-Knowledge-Catalog/blob/83b4625d847d4f0be219a166a9308034245ba274/LICENSE)
