# Icon Production & Identity Audit — 2026-09-30

## Repositories

- cn-wanmei/Popular-Rules-Icon
- cn-wanmei/Popular-Rules-Collection

## Canonical identity

Collection main `rule/_index.yaml` currently contains 394 entries with `entity: service`.
Icon dist release `icon-2026.09.30.r14` contains 482 entries.
Against the Collection canonical set, 393 are present, 1 canonical service (`ai`) is missing, and 89 entries are orphaned.

## Documentation drift found

1. R14/R20 status documentation simultaneously described R14 as done and in progress.
2. Release pointers called 482 entries 100% Collection coverage, which is not valid after canonical service filtering.
3. Collection V6 configuration/docs referred to `styles8` and `freeze1`, while the actual dist manifest is `r14`.
4. Collection V5 documents still described V5 as active/production.
5. Collection V5 automation could continue changing the V5 asset tree.

## Production-chain defects

1. Dist manifest variant metadata records `.bin` paths while physical dist artifacts are `.png`.
2. The configured `styles8` manifest did not exist on the dist branch; the actual published manifest was `r14`.
3. Icon `release.yml` and `incremental.yml` on main are placeholder/scaffold workflows rather than a reproducible publish writer.
4. Dist branch is present, but end-to-end reproducibility of its publication is not established by mainline workflow.
5. V5 fallback is still enabled, so deleting the V5 tree would remove the current safety path before all V6 gates are green.

## Decisions

- V5 cannot yet be removed.
- V5 automatic mutation workflows are retired on the migration branch.
- Collection remains the sole service identity authority.
- Icon registry normalization continues against the pinned Collection snapshot.
- A corrective immutable dist manifest release is required before declaring the V6 release path healthy.

## Completion conditions

Identity: 394/394 canonical services, zero production orphans.
Release: immutable manifest points to existing `.png` objects, resolver verified, reproducible release writer present.
Cutover: zero V5 fallback, zero V5 active references, rollback independent of V5 local tree.