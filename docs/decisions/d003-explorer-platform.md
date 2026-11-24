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

Defer selection **and implementation of the standalone Explorer UI** until Battalion has sufficient capability to support creating that UI. M0 does not require an Explorer UI or evaluation of UI frameworks and editors. When the capability gate is met, evaluate at least:

- A native-packaged desktop application, potentially using Tauri.
- A locally hosted web interface with a local backend.
- Other approaches only when they provide a meaningful fit advantage.

This deferral is not an endorsement of Tauri, React, Rust, or any other implementation stack. The Explorer's platform remains **undecided**.

# Rationale

Prematurely choosing a UI/runtime stack risks optimizing for familiarity or novelty before validating actual filesystem, indexing, distribution, and learning requirements. The Engineering Profile and OKF compatibility work are useful independently of a standalone UI; Battalion can produce and consume conforming documents without waiting for one.

# Consequences

- The M0 closeout keeps this deferral in force. The next milestone tests an exchange of Markdown files with Battalion using the existing reader. That exchange can proceed independently of a presentation platform. [M0 findings and follow-on scope](../compatibility/m0-findings.md)
- M0 focuses on format conformance, portable parsing, and the evidence-based indexing evaluation; standalone UI evaluation and implementation are not M0 exit requirements.
- Battalion is an anticipated producer and consumer of profiled artifacts, but neither Lattivra format conformance nor its tooling depends on Battalion.
- Any proof-of-concept interface must be disposable and must not establish an accidental technology commitment.
- Preserve a replaceable application/indexer boundary so platform and indexing selections can be made independently.

# Revisit Trigger

Revisit UI platform selection **only once Battalion can support creating the Explorer UI** and the maintainer elects to resume that work. Then compare alternatives for filesystem access, security, packaging, testability, cross-platform maintenance, offline operation, and portfolio learning value. M0 backend findings may inform that evaluation but do not themselves trigger UI development. Record a new explicit platform selection or amendment before production Explorer UI implementation.

The Atteniv evaluation was removed from M0 scope ([issue #6](https://github.com/lrburkholder/lattivra/issues/6), closed as not planned). This defers that evaluation; it does not choose or prohibit a future UI framework.

# References

- [Explorer specification](../specifications/explorer.md)
- [M0 compatibility plan](../plans/m0-compatibility.md)
