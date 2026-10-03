# Security Policy

> **Status: Current**  
> Popular-Rules-Icon is the Icon System V6 asset layer. It **consumes** Collection identity; it does not define `service_id`.

## Reporting

Report security issues via GitHub private vulnerability reporting or the repository owner.

## Controls

| Topic | Policy |
|-------|--------|
| Identity authority | Collection `rule/_index.yaml` only |
| Actions pin | Full SHA — align with Collection `docs/ACTIONS_SHA_PIN.md` |
| Permissions | Prefer `contents: read` on build/gate jobs; `write` only on publish |
| Dist objects | Content-addressed `dist/v/<sha256>.png`; no overwrite of immutable objects |
| Production pointer | `config/release-pointers.yaml` — independent rollback pointer |
| Secrets | Actions Secrets only |
| User packages | Icon Style GitHub Release Packages are manual `workflow_dispatch` only |

## Related

- Collection identity + pin table: [Popular-Rules-Collection](https://github.com/cn-wanmei/Popular-Rules-Collection)
- Source evidence layer: [Popular-Rules-Source](https://github.com/cn-wanmei/Popular-Rules-Source)
