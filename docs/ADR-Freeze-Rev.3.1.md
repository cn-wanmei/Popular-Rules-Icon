# ADR-Freeze-Rev.3.1 — Architecture Freeze

**Status:** FROZEN  
**Date:** 2026-09-29  

This document is the sole engineering baseline for Popular-Rules-Icon 6.0.

## Freeze declaration

1. Architecture is frozen. Implementation follows this document.
2. Conflicting legacy docs are superseded (see `docs/archive/`).
3. Features not listed here (OCR, embedding, runtime lazy render, CI scrape of Play/MS Store) are deferred past R1.0.

## Explicitly abolished

- GitHub Release mass assets as primary variant distribution
- Icon URLs embedding release tags
- Placeholder counting as Tier-0 real coverage 100%
- CI runtime scraping Google Play / Microsoft Store
- Naive stop-on-first-acceptable permanently locking weaker sources
- Large binaries on `main` history
- `content_hash` bound to ETag/URL
- Default full-service × all-styles every run
- AI upscaling presented as original source
- FULL meaning force-redownload

## Three surfaces

| Surface | Content | Writer |
|---------|---------|--------|
| `main` | schema, docs, registry, config, policies, code | humans + PR |
| `state` branch | fingerprints, run cursors, failures (sharded files) | bot only |
| `dist` (branch/Pages/object store) | `/v/{variant_hash}` | release job |

## Hash formulas

```
object_hash  = SHA256(canonical_bytes)
variant_hash = SHA256(object_hash + renderer_ver + style + size + format + policy_ver)
content_hash = SHA256(normalized_bindings + schema_ver + renderer_ver + policy_ver + canon_ver)
source_fingerprint = Hash(url + etag + last_modified + content_length)  # probe only
```

URL form: `/v/{variant_hash}` — never includes release tag.

## Coverage

- `coverage_real`: Tier-0 non-placeholder, quality OK — must be 100% for full release
- `coverage_placeholder`: counted separately
- `waiver`: expiry + owner + reason required

## Acquisition authority scores (score_rules_version: 1)

| class | score | locked |
|-------|------:|:------:|
| manual_review | 1000 | yes |
| curated_seed | 900 | yes |
| official_svg | 800 | no |
| official_page | 700 | no |
| third_party_allowlist | 500 | no |
| low_res_favicon | 100 | no |
| placeholder | 0 | no |

## ADR index

ADR-1 storage · ADR-2 hash · ADR-3 service_id · ADR-4 variant URL · ADR-5 license ·  
ADR-6 state branch · ADR-7 versioning · ADR-8 lifecycle · ADR-9 distribution_policy ·  
ADR-10 logical/physical manifest · ADR-11 reconstruction · ADR-12 score rules ·  
ADR-13 evidence · ADR-14 policy snapshot · ADR-15 rollback · ADR-16 lock granularity · ADR-17 failure taxonomy

See full planning document in repository history / project docs for narrative detail.
