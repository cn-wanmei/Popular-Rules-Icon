# R14–R20 Status (2026-09-30)

| Phase | Status | Notes |
|-------|--------|-------|
| R14 Collection coverage | **audit reopened** | Current dist has 482 entries; 393/394 current Collection canonical services are present, 89 entries are orphaned, and `ai` is missing. |
| R15 Style QA gate | **implemented** | 8 styles × 2 sizes are present in the R14 physical manifest; production validation is still required. |
| R16 Demand styles | **implemented** | `config/icon-demand.yaml` defines generic/rich subsets. |
| R17 Evidence bulk | **implemented** | Evidence tooling is present; provenance must be retained for canonical services. |
| R18 URL map export | **implemented** | URL map tooling exists; current manifest/path consistency requires validation. |
| R19 Mirror health | **implemented** | Mirror health tooling exists; no healthy release-chain proof yet. |
| R20 Yearly freeze | **pending** | Do not declare the current R14 dist a clean canonical freeze until identity and release gates pass. |

## Current truth

- `main` is the source of code/schema/registry/policies.
- `dist` currently contains release `icon-2026.09.30.r14`.
- The production pointer exists, but current canonical Collection coverage is 393/394, not 482/482.
- The project remains in migration: identity normalization and end-to-end release validation are not complete.