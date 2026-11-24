---
okf_version: "0.3"
title: Lattivra Project Knowledge
description: Project specifications, decisions, and plans for Lattivra.
license: Apache-2.0
---

# Lattivra project knowledge

## Profile

- [Engineering Profile specification](profiles/engineering/profile.md) — minimal conventions for engineering artifacts.

## Specifications

- [Explorer specification](docs/specifications/explorer.md) — read-only cross-project artifact discovery.
- [Foundation and interoperability specification](docs/specifications/foundation.md) — boundaries and shared requirements.

## Decisions

- [D-001: provisional project name](docs/decisions/d001-foundation.md) — Lattivra as the working umbrella name.
- [D-002: Apache-2.0 license](docs/decisions/d002-license.md) — licensing for project code, documentation, and profile text.
- [D-003: defer Explorer platform selection](docs/decisions/d003-explorer-platform.md) — defer standalone UI work until Battalion can support creating it; platform choice remains open.
- [D-004: defer indexing engine selection](docs/decisions/d004-indexing-engine.md) — Catalog lookup and refresh findings, adaptation costs, and conditions for reconsideration.
- [D-005: minimal Markdown-first Engineering Profile](docs/decisions/d005-profile-format.md) — build on native OKF conventions.
- [D-006: cross-source identity](docs/decisions/d006-cross-source-identity.md) — bundle-scoped identity and explicit cross-source mappings.
- [D-007: bundle discovery](docs/decisions/d007-bundle-discovery.md) — explicit bundle roots under configured sources.
- [D-008: initial types](docs/decisions/d008-initial-types.md) — Specification, Decision, and Implementation Plan.
- [D-009: validation policy](docs/decisions/d009-validation-policy.md) — separate OKF conformance, profile conformance, and link diagnostics.
- [D-010: defer dynamic external profile loading](docs/decisions/d010-external-profile-support.md) — keep third-party profile loading outside the MVP.
- [D-011: repository organization](docs/decisions/d011-repository-organization.md) — one monorepo with independently usable components.

## Plans

- [M0 compatibility proof of concept](docs/plans/m0-compatibility.md)

## Compatibility

- [M0 findings and proposed M1 exchange](docs/compatibility/m0-findings.md) — tested revisions, fixture outcomes, remaining gaps, and Battalion interoperability.
- [Pinned OKF v0.3 contract and conformance checklist](docs/compatibility/okf-v0.3-conformance.md) — baseline revision, expected behavior, and unresolved interpretations for M0.
- [M0 fixture harness and continuous verification](docs/compatibility/m0-harness.md) — commands, expected fixture outcomes, CI reports, and remaining coverage gaps.
- [Open Knowledge Catalog evaluation](docs/compatibility/open-knowledge-catalog.md) — observed multi-bundle search, navigation, refresh and rebuild results for v0.1.0.
