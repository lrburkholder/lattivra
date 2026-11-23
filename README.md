# Lattivra

Lattivra is an experimental, local-first, open-source project for exploring Open Knowledge Format (OKF) artifacts across independent sources. It is a personal portfolio and engineering learning project with two independently usable components:

- **Lattivra Explorer** — a planned read-only browser for discovering, searching, and navigating ordinary OKF artifacts across multiple local bundles.
- **Lattivra Engineering Profile for OKF** — minimal Markdown conventions for `Specification`, `Decision`, and `Implementation Plan` documents.

## Current status

The repository foundation includes the bootstrap Engineering Profile, project specifications, decision records D-001 through D-011, and the M0 compatibility plan. These documents form an OKF v0.3 bundle and use the profile to document Lattivra itself.

The Explorer and compatibility proof of concept are not implemented yet. M0 will establish parsing, indexing, search, and link-resolution behavior using independent fixture bundles. Explorer platform and indexing engine selection remain deferred until compatibility evidence is available.

The Explorer must remain useful without the Engineering Profile; the profile must be usable without the Explorer. Neither component depends on Battalion. The planned initial Explorer will read registered source files without modifying them and build disposable indexes. Native Markdown may be authoritative; a Markdown projection may derive from an authoritative upstream record.

## Documentation

- Start with [the OKF bundle index](index.md).
- Read the [Engineering Profile](profiles/engineering/profile.md).
- Review the [Explorer requirements](docs/specifications/explorer.md) and [foundation and interoperability requirements](docs/specifications/foundation.md).
- Browse all [11 decision records](index.md#decisions).
- Read the [M0 compatibility plan](docs/plans/m0-compatibility.md) for the technical approach and verification criteria.

## Work tracking

[GitHub Issues](https://github.com/lrburkholder/lattivra/issues) is the operational task tracker. Track work, progress, and completion there. Markdown plans describe the technical approach; specifications, decisions, and experiment results remain in the repository.

## Standards baseline

The format baseline is [OKF v0.3](https://github.com/open-knowledge-format/open-knowledge-format/blob/main/SPEC.md).

Normative reference reviewed at upstream Git blob `0dc3f7aa0fc710e588ba918eb115935d41eb2943` on 2026-11-22. The profile remains experimental and may evolve before its first stable release.

## Licensing

Project code, original documentation, and profile text are licensed under [Apache-2.0](LICENSE), unless otherwise noted. Review any third-party license notices before copying upstream implementation code.
