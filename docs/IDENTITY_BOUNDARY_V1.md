# Service Identity Boundary

> **Status: Current (Final for V6 clean production)**  
> Authority: Collection `rule/_index.yaml` · Icon `config/collection_identity_snapshot.json` · `config/release-pointers.yaml`  
> Historical phase checklist below is retained only as completed record — not as open work.

## Authority

**Popular-Rules-Collection** is the sole authority for canonical service identity (`service_id`, `display_name`, `provider`).

Icon Registry is an **identity consumer**. It must not rename, merge, invent, or reinterpret Collection services.

Pinned consumer snapshot:

| Field | SSOT |
|-------|------|
| Collection identity | `rule/_index.yaml` (entity=service only) |
| Icon pinned snapshot | `config/collection_identity_snapshot.json` |
| Production / rollback | `config/release-pointers.yaml` |

## Invariants

- file stem == `service_id`
- `service_id` exists in the pinned Collection snapshot
- registry name == Collection `display_name`
- registry provider == Collection `provider`
- aggregate/category entries never count as canonical service coverage
- shared image bytes do not imply shared service identity

## Final state (Clean V6)

| Phase | Outcome |
|-------|---------|
| A — Contract | **complete** |
| B — Pinned snapshot + report gate | **complete** |
| C — Registry normalization | **complete** (clean production registry) |
| D — Asset identity review | **complete** (orphan production identities removed; audit retained) |
| E — Strict CI | **complete** (V6 strict gates in PR CI / release writer) |

See also:

- `docs/PRODUCTION_IDENTITY_AUDIT_2026-09-30.md`
- `README.md` (system boundaries; no handwritten coverage counts)

## Freshness (consumer obligation)

Collection remains identity authority. Icon must keep the pinned snapshot **verifiably fresh**:

```text
Collection rule/_index.yaml
        ↓
compare to config/collection_identity_snapshot.json
        ↓
NO DRIFT → PASS
DRIFT    → open sync PR (scripts/sync_collection_identity_snapshot.py)
```

Do not treat a matching service *count* alone as proof of identity currency — always compare content / source ref.
