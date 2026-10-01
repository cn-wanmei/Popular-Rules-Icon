# Popular-Rules-Icon

> Icon System 6.0 — independent, content-addressed, immutable-manifest icon infrastructure for the Popular-Rules ecosystem.

## 当前状态 — 2026-09-30

| 项目 | 状态 |
|---|---|
| Collection identity authority | `cn-wanmei/Popular-Rules-Collection/rule/_index.yaml` |
| Canonical services | **394** |
| Active V6 release | `icon-2026.09.30.clean1` |
| Canonical coverage | **394/394 (100%)** |
| Production orphan identities | **0** |
| Variant matrix | **6304** (394 services × style/theme matrix; see release manifests; `styles: 8` in release-pointers) |
| Manifest physical closure | **6304/6304** |
| Clean release-writer build-and-gate | **PASS** |
| Clean release-writer publish | **PASS** |
| V6 fallback | **Collection fallback disabled; Icon strict V6 only** |
| Independent rollback | `icon-2026.09.30.clean1-rb1` |
| V5 production registry | **removed from Icon production state** |

## 身份边界

Popular-Rules-Collection owns canonical `service_id`, `display_name`, and `provider`.
Icon Registry consumes those identities and only binds icon assets.

The current clean production Registry contains exactly the 394 canonical Collection service IDs.
Historical/orphan production identities were removed from production and retained in audit history.

## 生产链

```text
Collection canonical identity
        ↓
Icon pinned identity snapshot
        ↓
state
        ↓
V6 release writer
        ↓
strict gates
        ↓
immutable dist release
        ↓
Collection V6 resolver
```

See `docs/PRODUCTION_IDENTITY_AUDIT_2026-09-30.md` and `docs/IDENTITY_BOUNDARY_V1.md`.

## Documentation

- [docs/INDEX.md](docs/INDEX.md)
