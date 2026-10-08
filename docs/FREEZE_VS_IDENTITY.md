# Freeze vs Identity Refresh

Production **pointer freeze** (`config/release-pointers.yaml` `frozen: true`) freezes only:

- `production` / `rollback` release IDs consumed by clients

It must **not** block:

- `config/collection_identity_snapshot.json` refresh
- identity-freshness compare / PR
- candidate manifest generation on non-production paths

## Contract

| Layer | During freeze |
|-------|----------------|
| Identity snapshot | may update |
| Release candidate | may generate |
| `production` pointer | frozen until expiry / explicit unfreeze |

## Trigger

- schedule identity-freshness
- `repository_dispatch` type `collection-identity-changed` (from Collection when `ICON_DISPATCH_TOKEN` configured)
