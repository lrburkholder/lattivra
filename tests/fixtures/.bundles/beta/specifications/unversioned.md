---
type: Specification
title: Synthetic projection without a source revision
sources:
  - id: authoritative-source
    resource: https://fixtures.example/battalion/requirements/SYNTHETIC-002
generated: { by: "fixture-exporter/0.1", at: "2026-06-19T00:00:00Z" }
---

# Context

The synthetic upstream requirement has no published revision.

# Requirements

Keep the upstream URI and producer attribution. Resolve the [local decision](/decisions/shared.md) within beta.

# Acceptance Criteria

The projected source entry omits the optional revision.
