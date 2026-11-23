---
type: Specification
title: M0 — Fixture Harness and Continuous Verification
status: draft
tags: [m0, fixtures, validation, ci]
---

# Context

The replaceable Python harness in [m0_harness](../../m0_harness/) implements the fixture and diagnostic experiments described in issues [#3](https://github.com/lrburkholder/lattivra/issues/3) and [#4](https://github.com/lrburkholder/lattivra/issues/4), against the [pinned OKF contract](okf-v0.3-conformance.md). Its dependencies are experiment tooling; [D-003](../decisions/d003-explorer-platform.md) and [D-004](../decisions/d004-indexing-engine.md) remain deferred.

# Requirements

## Local reproduction

Use Python 3.14. From the repository root on Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-m0.txt
.\.venv\Scripts\python.exe -m pytest -q --junitxml=artifacts/pytest.xml --contract-report=artifacts/checklist-coverage.json
.\.venv\Scripts\python.exe -m m0_harness tests/fixtures/corpus.json --output artifacts/conformance.json
```

On Linux/macOS use `.venv/bin/python` for the three virtual-environment commands. Dependencies are pinned in [requirements-m0.txt](../../requirements-m0.txt). Installed packages are `ruamel.yaml` for safe YAML 1.2 parsing and duplicate-key rejection, `markdown-it-py` plus its footnote plugin for Markdown tokenization, and `pytest` for assertions. No imported asset, executor, or attester is executed.

## Fixtures and results

The [fixture inventory](../../tests/fixtures/README.md) describes the independent roots. [corpus.json](../../tests/fixtures/corpus.json) is the reviewable expected-result oracle, separate from the reader implementation. Profile selection and legacy path fallback are explicit registration settings. URI mappings use registered bundle ID plus native concept path; there is no global ID requirement or automatic nested-bundle discovery.

The CLI hashes the inventory and the files under each declared fixture bundle before and after scanning, including bundles stored outside the inventory directory. The report uses inventory-relative paths for files beneath that directory and records the configured paths for external files. The CLI exits with status 0 when expected results match, 1 for expectation mismatches, or 2 for an invalid invocation/configuration. Reports must be written outside the fixture directory and all configured roots. It also records the pinned upstream commit/blob, harness Git revision, whether its checkout has local changes, installed parser versions, fixed evaluation clock, file hashes, discovered concepts, metadata, directed relationships, and diagnostics. Incoming relationships can be derived from those edges; this is not a persistent search index.

An intentionally invalid fixture can produce a successful test run. For example, alpha's duplicate YAML key must cause a format diagnostic while its valid neighbors remain discoverable. The format verdict for alpha remains false in the report; a matching expected failure never turns it into a valid bundle.

Results remain independent:

- `conformant` considers format diagnostics only.
- Each concept's `profile` is `not_applied`, `passed`, or `failed`; a profile failure does not change its format verdict.
- Reference, compatibility, metadata, access, configuration, and type-specific producer-contract diagnostics remain separate categories.
- Trust and staleness are derived metadata with an explicit clock. An input file never proves that a computation run was attested.

## Checklist traceability and limits

`artifacts/checklist-coverage.json` records actual test outcomes under each stable checklist ID. `exercised` means at least one mapped example passed; it does not certify every variant in that checklist row. The report also lists failures, skips, pending rows, and all eight unresolved interpretations. Review JUnit output for individual parameter cases.

The current tests exercise discovery, frontmatter parsing, reserved-file boundaries, extension retention, optional-value normalization, projection provenance, paths/URI mappings, graph edges, trust/staleness, selected profiles, static computation lookup, and filesystem/registration boundaries. The following checklist rows remain pending:

| IDs | Remaining work |
| --- | --- |
| RES-04, RES-05 | Directory-listing semantics and producer index regeneration. The read-only harness never rewrites an index. |
| FM-07, FM-08 | Dedicated body-dialect checks and producer editing/serialization recommendations. Markdown tokenization is used, but these rows have no dedicated assertions yet. |
| META-05, META-06 | Per-claim source-ID attribution and credibility-window interpretation. Raw metadata is retained. |
| STATE-05 | Following lifecycle replacements, including missing targets and cycles. The path is resolved but replacements are not followed. |
| VER-05 | Optional legacy timestamp/citation-body fallbacks. |

Unresolved cases retain the contract's U-01 through U-08 labels. For U-01 the harness provisionally skips null/empty `type` values as absent, and reports other malformed types as unresolved; this is local policy rather than a universal conformance ruling. Unknown custom YAML tags and recursive aliases are unsupported compatibility cases, and missing generation timestamps do not produce an invented human-reviewed tier. Source scope descriptors use a provisional whitespace heuristic; ambiguous unencoded paths need policy review. In-root filesystem aliases are skipped with a compatibility diagnostic rather than traversed. The timestamp parser uses Python's date-time support and does not implement RFC 3339 leap seconds. These limits must not be reported as full OKF consumer conformance.

Candidate backend evaluation, persistent indexing, search, incremental refresh/rebuild, and Explorer UI remain subsequent M0 work. The harness makes no claim that those capabilities have been tested.

## GitHub Actions

[M0 conformance](../../.github/workflows/m0-conformance.yml) runs the same commands on pull requests, pushes to `main` (including merges), and manual dispatch. Linux and Windows jobs use Python 3.14, pinned dependencies, and commit-pinned GitHub actions. The workflow has read-only repository permissions and uploads JUnit, checklist traceability, and the fixture report for 14 days, including on test failure where installation succeeded.

Linux must run the actual symlink escape test; an OS error there fails the test. Windows runs a junction escape/alias-registration test and attempts the symlink test, which may skip if the user lacks symlink privileges. A local sandbox may block junction creation; in that environment the filesystem test needs an unrestricted test run. Skips remain visible in the reports.

The action does not fetch a moving upstream spec or rewrite expectations. Enabling a required branch-protection check is a separate repository setting; merely adding this workflow does not block merges. Hosted execution begins when these files are pushed to GitHub.

# Acceptance Criteria

1. The inventory's expected discovery, profile, diagnostic, and reference outcomes are asserted, and valid neighbors survive malformed files.
2. Duplicate native concept paths across independently registered bundles remain distinct.
3. Fixture hashes match before and after reading; reports cannot overwrite fixture inputs.
4. The report identifies the normative baseline, tool revision, fixed clock, supported examples, pending checks, and skips.
5. The same documented test and fixture-report commands run in local and GitHub Actions environments.
