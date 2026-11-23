---
type: Decision
title: D-008 — Bootstrap Three Engineering Artifact Types
status: stable
tags: [profile, types, scope]
---

# Context

Lattivra needs to document itself using the profile, but implementing a comprehensive engineering taxonomy before having working artifacts would be premature.

# Decision

**Decision ID:** D-008. **Approval:** accepted.

The initial type names are exactly `Specification`, `Decision`, and `Implementation Plan`. Each is a regular OKF concept with human-readable Markdown sections. No separate schemas are required for authoring at this stage.

- Specification: Context, Requirements, Acceptance Criteria.
- Decision: Context, Decision, Rationale, Consequences.
- Implementation Plan: Objective, Tasks, Verification.

# Rationale

These support the project's immediate documentation needs and provide realistic materials for profile dogfooding and compatibility testing.

# Consequences

- Engineering Knowledge, Review Finding, and Verification Evidence are deferred as distinct types.
- Conformance to these three types is an additional profile-level check, not a prerequisite for OKF v0.3 conformance.
- The type list and heading conventions remain experimental until profile versioning is stabilized.

# References

- [Engineering Profile](../../profiles/engineering/profile.md)
