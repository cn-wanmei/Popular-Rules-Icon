# Icon Production & Identity Audit — 2026-09-30

## Repositories audited

- `cn-wanmei/Popular-Rules-Icon`
- `cn-wanmei/Popular-Rules-Collection`

## Canonical identity

Collection main `rule/_index.yaml` currently exposes 394 entries with `entity: service`.
Icon production must use that canonical service universe; aggregate/category records are not substitute services.

## Current V6 publication

`dist` contains release `icon-2026.09.30.r14`; a corrected immutable manifest `icon-2026.09.30.r14.1` was added without changing the original R14 manifest.

Manifest inventory:
- 482 entries;
- 16 variant keys per entry;
- 7712 variant records;
- 393/394 current Collection service IDs present;
- missing canonical service: `ai`;
- 89 entries are orphaned relative to the current Collection service identity.

## Documentation/configuration drift found

1. Collection V6 configuration referenced a non-existent `styles8` manifest; migration branch now points to `r14.1`.
2. Cutover documentation referenced `freeze1`; migration branch now records `r14.1`.
3. Collection V5 documents described V5 as active production even though provider was V6; migration branch marks V5 legacy fallback only.
4. Collection README advertised the V4 icon library; migration branch switches the active reference to V6.
5. Three V5 mutation workflows were retired on the migration branch.
6. R14 release pointers called 482 entries 100% Collection coverage; the migration branch records canonical 393/394.
7. The original R14 manifest recorded `.bin` paths while physical dist objects are `.png`; R14.1 and the manifest writer are corrected to `.png`.
8. Icon R14/R20 documentation contradicted itself about completion; migration branch reconciles the state.

## Production-chain assessment

**Not healthy end-to-end yet.**

Verified:
- dist branch exists and contains content-addressed PNG objects;
- R14.1 manifest exists;
- 8 styles × 128/256 variant records exist;
- repository PR CI has passed its current tests and freeze/metrics checks.

Unverified/blocking:
- reproducible release writer in mainline CI is absent; `release.yml` is currently a placeholder;
- current release publication is not proven reproducible from source + workflow;
- resolver end-to-end against the corrected immutable manifest is not yet gated;
- canonical service identity is 393/394, with 89 orphans;
- V5 fallback remains enabled.

## V5 removal

Do **not** remove V5 yet.

V5 removal requires all of:
1. 394/394 canonical Collection services in V6;
2. zero production orphans;
3. zero V5 fallback use;
4. resolver end-to-end verification;
5. manifest paths equal physical object paths;
6. reproducible release writer + validation;
7. zero active V5 references in Collection;
8. rollback independent of V5 local assets.

Until then, V5 is frozen as a safety net and must not receive new automatic writes.

## Identity-boundary progress

Phase A — contract: complete.
Phase B — pinned Collection snapshot + gate: complete.
Phase C — Icon Registry normalization: in progress.
Phase D — seed/asset identity review: pending.
Phase E — strict CI: blocked until C and D are clean.
