# Lattivra

Lattivra is an experimental, local-first, open-source project centered on portable Open Knowledge Format (OKF) engineering artifacts and their exploration across independent sources. It is a personal portfolio and engineering learning project with two independently usable components:

- **Lattivra Explorer** — a future read-only browser for discovering, searching, and navigating ordinary OKF artifacts across multiple local bundles; standalone UI development is deferred.
- **Lattivra Engineering Profile for OKF** — minimal Markdown conventions for `Specification`, `Decision`, and `Implementation Plan` documents.

## Current status

The repository foundation includes the bootstrap Engineering Profile, project specifications, decision records D-001 through D-011, and the M0 compatibility plan. These documents form an OKF v0.3 bundle and use the profile to document Lattivra itself.

The M0 harness verified independent OKF bundles, bundle-scoped identities, and read-only consumption. Open Knowledge Catalog v0.1.0 lost a shared decision on lookup and retained stale search results after an edit. Indexing-engine selection remains deferred. The proposed M1 milestone exchanges a profiled Markdown artifact with Battalion. Standalone Explorer UI work remains deferred until Battalion can support building it. [M0 findings and reproduction instructions](docs/compatibility/m0-findings.md)

The Explorer must remain useful without the Engineering Profile; the profile must be usable without the Explorer. Neither component depends on Battalion. Battalion is an anticipated primary producer and consumer of conforming engineering artifacts, not the owner of the format. The profile and OKF compatibility tooling provide value without a standalone UI. The planned Explorer will read registered source files without modifying them and build disposable indexes. Native Markdown may be authoritative; a Markdown projection may derive from an authoritative upstream record.

## Documentation

- Start with [the OKF bundle index](index.md).
- Read the [Engineering Profile](profiles/engineering/profile.md).
- Review the [Explorer requirements](docs/specifications/explorer.md) and [foundation and interoperability requirements](docs/specifications/foundation.md).
- Browse all [11 decision records](index.md#decisions).
- Read the [M0 compatibility plan](docs/plans/m0-compatibility.md) for the technical approach and verification criteria.
- Use the [pinned OKF v0.3 contract and conformance checklist](docs/compatibility/okf-v0.3-conformance.md) for fixture expectations and tool evaluation.
- Run the [M0 fixture harness](docs/compatibility/m0-harness.md) locally and review its CI reports, coverage limits, and reproduction commands.

## Work tracking

[GitHub Issues](https://github.com/lrburkholder/lattivra/issues) is the operational task tracker. Track work, progress, and completion there. Markdown plans describe the technical approach; specifications, decisions, and experiment results remain in the repository.

## Standards baseline

The format baseline is [OKF v0.3 at upstream commit `527e81a`](https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md).

Normative reference reviewed on 2026-11-22: commit `527e81aff55992be21507e97004286789126f88c`, `SPEC.md` Git blob `0dc3f7aa0fc710e588ba918eb115935d41eb2943`. See the [conformance checklist](docs/compatibility/okf-v0.3-conformance.md) for the contract, optional behavior, and unresolved interpretations. The profile remains experimental and may evolve before its first stable release.

## Licensing

Project code, original documentation, and profile text are licensed under [Apache-2.0](LICENSE), unless otherwise noted. Review any third-party license notices before copying upstream implementation code.
