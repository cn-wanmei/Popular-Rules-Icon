# Icon Production & Identity Audit — 2026-09-30

`Popular-Rules-Collection/rule/_index.yaml` is the sole service-identity authority.
Final Collection production commit: `c2f6676e44b6a3641a5a5d06c79644e0935faf86`.
Canonical service universe: 394.

## Clean V6 release
- `icon-2026.09.30.clean1`;
- canonical entries: 394/394;
- production orphan identities: 0;
- `ai` present with canonical provider `special`;
- 6304 variant records;
- physical object closure: PASS;
- strict manifest gate: PASS;
- release-writer build-and-gate: PASS;
- release-writer publish: PASS.

## Historical/orphan cleanup
89 historical/orphan production identities were removed from Icon production state and retained only in `reports/orphaned-production-identities-2026-09-30.json`.

## Rollback
Independent immutable V6 rollback: `icon-2026.09.30.clean1-rb1`.
It has no dependency on Collection V5 assets.

## Production chain
Collection canonical identity → pinned Icon snapshot → exact state → release writer → strict manifest gate → physical object closure → immutable dist.
The clean release-writer path is proven. The separate incremental acquisition workflow remains scaffolded and is not the production path used for clean1.

## V5 retirement
Collection `fallback_to_v5` is disabled, V5 runtime code/configuration has been removed, the V5 retirement conditions passed by direct live-repository verification, and `assets/icons/v5` has been physically deleted.

## Final identity-boundary state
- Collection: sole identity authority.
- Icon Registry: 394 canonical service IDs only.
- Identity gate: strict.
- No production orphans.
- No V5 runtime dependency.
- Collection V5 asset tree: deleted.
- R20 final Collection retirement: complete.
