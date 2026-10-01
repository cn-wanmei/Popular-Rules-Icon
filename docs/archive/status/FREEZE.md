# Icon Freeze Declaration

## freeze_id
`icon-2026.09.30.freeze1`

## What is frozen
1. **Source images** in `assets/icons/seed/<service_id>.*` (one file per service)
2. **Content-addressed objects** in `assets/icons/objects/<object_hash>.*`
3. **PNG variants** on `dist` branch: `v/<variant_hash>.png` (128 + 256)
4. **config/official_sources.yaml** points to `seed://...` only (`source_class: frozen_seed`)
5. **config/remote_provenance.yaml** keeps original remote URLs for audit (not fetched)

## Runtime behavior
- `acquire-canary` loads `seed://` from local disk; no network for frozen services
- CDN delivery remains content-addressed: `https://cdn.jsdelivr.net/gh/cn-wanmei/Popular-Rules-Icon@dist/v/{variant_hash}.png`

## How to change an icon after freeze
1. Replace file under `assets/icons/seed/`
2. Update or keep `seed://` entry
3. Re-run acquire + republish dist
4. Bump freeze_id / release pointer

## Reviewer sign-off
- RISK_REVIEW manual replacements applied
- User declared: 定稿，固化远程图
