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

## Rollback pointer and manifest reconciliation — 2026-11-10
The active rollback pointer is `icon-2026.09.30.clean1`, matching both Icon
`config/release-pointers.yaml` and Collection `config/icon_v6.yaml`.

Read-only verification against the immutable `dist` tree:
- Production `icon-2026.10.06.full1`: 394 entries, 6,304 variant records,
  5,840 unique variant files; all referenced variant files exist.
- Rollback `icon-2026.09.30.clean1`: 394 entries, 6,304 variant records,
  5,184 unique variant files; all referenced variant files exist.
- Historical alias `icon-2026.09.30.clean1-rb1`: same content hash and identical
  394-entry manifest payload as `clean1`; all referenced variant files exist.
  It is not selected by either current pointer.

The rollback release is independent of Collection V5 assets. No production or
rollback pointer was changed during this audit.

## Automated pointer and closure gate
`scripts/release_pointer_closure_gate.py` validates both configured pointers
against the immutable `dist` branch, checks all canonical identities, the full
16-variant matrix per service, and the existence of every referenced PNG.
PR CI runs this gate before changes can merge.

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
