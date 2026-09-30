# Popular-Rules-Icon

> Icon System 6.0 — independent, incremental, content-addressed, immutable-manifest icon infrastructure for the Popular-Rules ecosystem.

## Current status — 2026-09-30

| Area | Status | Verified state |
|---|---|---|
| Collection identity authority | **in migration** | Collection `rule/_index.yaml` is canonical |
| V6 dist | **exists** | `icon-2026.09.30.r14.1` corrected manifest is published on `dist` |
| Canonical service coverage | **blocked** | 393/394 current Collection services present; `ai` missing |
| Production orphan entries | **blocked** | 89 dist/registry IDs are not current Collection services |
| Variant matrix | **present** | 8 styles × 128/256 = 16 variants per manifest entry |
| Release writer | **implemented / fail-closed** | main `release.yml` now builds from exact state snapshot and blocks on identity/variant/object gaps |
| V5 removal | **blocked** | V5 remains Collection fallback/rollback safety net |
| R20 yearly freeze | **pending** | requires identity + release gates |

## Authority boundary

Popular-Rules-Collection owns canonical `service_id`, `display_name`, and `provider`.
Icon Registry only binds icon assets to those identities. It must not invent, rename, merge, or reinterpret services.

See `docs/IDENTITY_BOUNDARY_V1.md` and `docs/PRODUCTION_IDENTITY_AUDIT_2026-09-30.md`.

## Surfaces

| Surface | Role |
|---|---|
| `main` | code, schema, registry, policies |
| `state` | bot fingerprints and cursors |
| `dist` | immutable content-addressed icon artifacts |

## Quick start

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m popular_rules_icon.cli fixture-run --svg tests/fixtures/geom_blue.svg
```

## License

Code: MIT (`LICENSE`). Brand icons: see `NOTICE` — not granted under MIT.
