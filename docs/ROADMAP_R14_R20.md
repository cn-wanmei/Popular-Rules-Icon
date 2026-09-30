# R14–R20 Plan

| Phase | Scope | Current state |
|-------|-------|---------------|
| R14 | Collection gap fill / identity boundary | **Enforced / backlog remains** — canonical Collection service universe is 394; existing 393 canonical registry identities are normalized; `ai` is still missing and 89 historical/orphan dist entries remain outside the canonical set. |
| R15 | Style QA gate | **Implemented** — 8 styles × 128/256 PNG variants. |
| R16 | Demand-driven subset | **Implemented**. |
| R17 | Evidence packs | **Implemented**, canonical registry normalization completed for the 393 existing service records. |
| R18 | URL map | **Implemented**, subject to manifest/physical consistency. |
| R19 | Mirror health | **Implemented tooling**, release health not yet proven end-to-end. |
| R20 | Immutable freeze | **Pending**. Requires strict identity + release gates. |

## Required sequence from here

Collection canonical identity → pinned snapshot → canonical registry normalization → resolve missing `ai` → retire 89 historical/orphan production entries → manifest/physical validation → first clean release-writer run → strict CI → V5 retirement gate.