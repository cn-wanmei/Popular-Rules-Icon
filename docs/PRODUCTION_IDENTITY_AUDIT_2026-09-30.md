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

1. Collection V6 configuration referenced a non-existent `styles8` manifest; current main points to `r14.1`.
2. Cutover documentation referenced `freeze1`; current main records `r14.1`.
3. Collection V5 documents described V5 as active production even though provider was V6; current main marks V5 legacy fallback only.
4. Collection README advertised the V4 icon library; current main switches the active reference to V6.
5. Three V5 mutation workflows were retired on the migration branch.
6. R14 release pointers called 482 entries 100% Collection coverage; the current main records canonical 393/394.
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
- reproducible release writer is now implemented in main `release.yml` as a fail-closed state→manifest writer; no clean production run has been published yet because current state is missing `ai`.
- a clean end-to-end publication run remains pending; the current state would intentionally be blocked by the canonical identity gate.
- resolver end-to-end against the corrected immutable manifest still needs a dedicated publication gate/run.
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
Phase C — Icon Registry normalization: canonical fields normalized for existing 393 records; one canonical service (`ai`) is still missing and historical/orphan cleanup remains in progress.
Phase D — seed/asset identity review: pending.
Phase E — strict CI: blocked until C and D are clean.
