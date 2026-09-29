# Implementation Progress

| Phase | Status | Notes |
|-------|--------|-------|
| R0.1–R0.4 | done | Freeze, schema, registry, L0/L1 |
| R1 | done | Canary acquire 10/10 |
| R2 | done | Hires App Store JPG/WEBP seeds + binding lock |
| R3 | done | dist content-addressed; **icon-2026.09.29.3** PNG 128/256 delivery |
| R4 | done | Collection `icon_v6.yaml` shadow (default v5) |
| R5 | pending | Default cutover after shadow acceptance |
| Expand | in progress | Registry 20 services (10 pending source URLs) |

## Current production pointer

`icon-2026.09.29.3` — App Store/brand sources + PNG delivery variants (max_upscale 1.0).

## Branches

- `main` — code, schema, registry, seeds
- `state` — per-service runtime state
- `dist` — `/v/{variant_hash}.png` + objects + manifests
