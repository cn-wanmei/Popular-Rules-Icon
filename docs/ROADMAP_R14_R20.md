# R14–R20 Plan

| Phase | Scope | Current state |
|-------|-------|---------------|
| R14 | Collection gap fill / identity boundary | **Reopened for audit** — canonical Collection service universe is 394; current dist has 393 canonical matches + 89 orphans. |
| R15 | Style QA gate | **Implemented** — 8 styles × 128/256 PNG variants. |
| R16 | Demand-driven subset | **Implemented**. |
| R17 | Evidence packs | **Implemented**, subject to identity normalization. |
| R18 | URL map | **Implemented**, subject to manifest/physical consistency. |
| R19 | Mirror health | **Implemented tooling**, release health not yet proven end-to-end. |
| R20 | Immutable freeze | **Pending**. Requires strict identity + release gates. |

## Required sequence from here

Collection canonical identity → Icon snapshot → registry normalization → asset identity review → manifest/physical validation → reproducible release writer → strict CI → V5 retirement gate.