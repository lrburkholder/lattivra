---
type: Decision
title: D-003 — Defer Explorer Platform Selection
status: stable
tags: [explorer, platform, deferred]
---

# Context

Lattivra Explorer must be local-first, support explicit access to multiple filesystem directories, run offline for core functions, and remain read-only in the MVP. The implementation platform has not been demonstrated or selected. Portfolio learning value matters alongside utility and maintenance cost.

# Decision

**Decision ID:** D-003. **Approval:** accepted decision to defer selection.

Do not select a desktop or web platform during the documentation bootstrap. Evaluate at least:

- A native-packaged desktop application, potentially using Tauri.
- A locally hosted web interface with a local backend.
- Other approaches only when they provide a meaningful fit advantage.

This deferral is not an endorsement of Tauri, React, Rust, or any other implementation stack. The Explorer's platform remains **undecided**.

# Rationale

Prematurely choosing a UI/runtime stack risks optimizing for familiarity or novelty before validating actual filesystem, indexing, distribution, and learning requirements.

# Consequences

- M0 should focus on portable parsing and indexing contracts rather than an Explorer UI.
- Any proof-of-concept interface must be disposable and must not establish an accidental technology commitment.
- Preserve a replaceable application/indexer boundary so platform and indexing selections can be made independently.

# Revisit Trigger

After the M0 compatibility proof of concept documents backend constraints and the maintainer's learning objectives are explicit, compare alternatives for filesystem access, security, packaging, testability, cross-platform maintenance, offline operation, and portfolio learning value. Record a new explicit platform selection or an amendment to this decision before production Explorer UI implementation.

# References

- [Explorer specification](../specifications/explorer.md)
- [M0 compatibility plan](../plans/m0-compatibility.md)
