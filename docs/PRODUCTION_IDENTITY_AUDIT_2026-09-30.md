# Icon Production & Identity Audit — 2026-09-30

## Canonical identity
Popular-Rules-Collection rule/_index.yaml is the sole service identity authority. Current canonical service universe: 394 services.

## Clean V6 release

The first clean release-writer publication completed successfully:

- release: icon-2026.09.30.clean1
- canonical entries: 394/394
- orphan entries: 0
- variant matrix: 8 styles × 128/256 = 16 per service
- variant records: 6304
- physical object closure: PASS / 0 missing
- strict V6 manifest gate: PASS
- release writer build-and-gate: PASS
- release writer publish: PASS

The release-writer run also materialized the missing AI seed-derived physical objects and published them together with the immutable manifest.

## Identity cleanup

Production registry/services has been reduced from 482 records to the 394 Collection canonical service IDs. The 89 removed historical/orphan identities are archived in reports/orphaned-production-identities-2026-09-30.json.

The separate Icon state branch has also been promoted to the canonical 394-service state and contains finalized ai state.

## Rollback

Production rollback is now an independent immutable V6 release:

icon-2026.09.30.r14.1

It does not depend on Collection V5 assets.

## V5

V5 fallback remains temporarily enabled in Collection until the Collection-side retirement gate is executed. No V5 asset deletion is performed in this Icon promotion change.

## Production-chain status

The V6 release-writer path is now proven for a clean release. The incremental acquisition workflow remains a separate unfinished automation surface and is not a prerequisite for this clean immutable publication.

Next: update Collection to use clean1, disable fallback_to_v5, pass the V5 retirement gate, then delete Collection assets/icons/v5.
