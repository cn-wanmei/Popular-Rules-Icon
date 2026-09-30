# Icon Production & Identity Audit — 2026-09-30

## Canonical service identity

`Popular-Rules-Collection/rule/_index.yaml` is the sole service-identity authority.

Current canonical service universe:
- 394 services;
- current Collection rule index SHA: `493eb3bcbb9e69c3067adeed336cc0e2566537a1`;
- Icon pinned snapshot references the current Collection main commit and the same rule-index SHA.

## Clean canonical V6 release

The first clean release-writer publication completed successfully:

- release: `icon-2026.09.30.clean1`;
- canonical entries: 394/394;
- orphan production identities: 0;
- variant records: 6304 = 394 × 16;
- physical object closure: 6304 referenced paths, 0 missing;
- strict V6 manifest gate: PASS;
- release-writer build-and-gate: PASS;
- release-writer publish: PASS;
- `ai` is present and materialized;
- clean manifest content hash: `2e17d9ea189bc2479895135bd36821fb6edf0fae52b8b9470e11a080be5b2ccf`.

The 89 historical/orphan production identities were removed from the production state/manifest. They remain represented in audit history, not in the canonical V6 production identity set.

## Rollback

Independent rollback release:
- `icon-2026.09.30.clean1-rb1`

It is an immutable V6 manifest-only rollback pointer over the already-verified clean1 physical objects and has no dependency on `Collection/assets/icons/v5`.

## Identity gate

Current production registry contains 394 canonical service IDs; the previous `ai.provider` metadata drift was corrected to `special`.

## V5

Icon side has no V5 runtime production dependency. Collection-side V5 fallback is being disabled in the final cutover; physical V5 assets are deleted only after the Collection retirement gate passes.

## Production-chain conclusion

The clean V6 production writer is proven for the canonical 394-service release:

Collection identity → pinned snapshot → exact state → release writer → strict manifest gate → physical object closure → immutable dist publish.

The separate incremental acquisition workflow remains a distinct automation surface and is not used by the clean release-writer publication.

## Final sequence

1. clean1 verified;
2. independent clean rollback published;
3. Collection switches to clean1 and `fallback_to_v5=false`;
4. Collection V5 retirement gate passes;
5. `assets/icons/v5` is physically deleted;
6. V5-only production references are removed;
7. Collection validation/publish gates are rerun.
