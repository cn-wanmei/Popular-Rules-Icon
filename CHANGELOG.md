# Changelog

## icon-2026.10.06.full1 — 2026-10-06

Full Icon Production Repair (promoted via PR #20).

- **Production**: `icon-2026.10.06.full1` (rollback: `icon-2026.09.30.clean1`)
- **Coverage**: 394/394 canonical services (100%)
- **Objects**: 6304 variant records (8 styles)
- Service identity boundary enforced (no parent-brand logo reuse for sub-services)
- Alias policy tightened (explicit visual aliases only: epicgames→epic, himalaya→ximalaya, tencentdocs→qqdoc)
- 50 service-specific source overrides (Simple Icons SVG preferred; official favicon fallback)
- Seed path reconciliation + content-addressed validation
- Microsoft / Apple / Mesh and related visual identity fixes
- Full rebuild with forced state object_hash/variant_hashes reset
- CI: Full Icon Production Repair #18 success; PR CI L0–L1 success on merge

Docs: `docs/FULL_ICON_REPAIR_2026-10-06.md`, `docs/ICON_VISUAL_SYSTEM_AUDIT_2026-10-06.md`

## 0.1.0 — 2026-09-29

- Architecture Freeze ADR-Rev.3.1 landed
- Schema, config, policies, registry samples (10 Tier-0)
- Core library: hash, sanitize, score, SSRF helpers, L1 pipeline
- PR CI L0–L1
