# Icon coverage & identity freshness gate

## Coverage definition (locked 2026-10-06)

Icon production coverage is measured **only** against Collection entries with:

```yaml
entity: service
```

Excluded by `collection_identity_snapshot.json` → `selection.exclude_entities`:

- `provider_aggregate`
- `aggregate`
- `domestic_aggregate`
- `category`

Therefore:

| Metric | Meaning |
|--------|--------|
| `canonical_collection_services` in `release-pointers.yaml` | count of `entity: service` in pinned snapshot |
| Collection `_index` total entries (e.g. 651) | includes aggregates — **do not** use as Icon denominator |
| `collection_coverage: 100% (394/394)` | full coverage of **services** |

## Freshness gate (required)

Before promoting a new production pointer:

1. Snapshot `source.ref` + `source.file_sha` must match a real Collection commit of `rule/_index.yaml`.
2. Recompute service set from that file with the same selection filter.
3. `canonical_services_missing == 0` and `orphan_entries == 0`.
4. If Collection added new `entity: service` rows since snapshot → open identity sync PR first (`scripts/sync_collection_identity_snapshot.py`).

## CI expectations

- Identity Freshness workflow should fail closed when snapshot service set ≠ filtered live `_index` (when freeze allows updates).
- During `frozen: true`, only document drift; do not mutate production pointer without ADR / freeze extension.

## Cross-repo

Collection documents the same口径 in `docs/SSOT_NUMBERS.md`.
