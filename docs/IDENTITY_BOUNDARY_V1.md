# Service Identity Boundary V1

## Authority

Popular-Rules-Collection is the sole authority for canonical service identity.

Pinned source: Collection main commit b95c01f98704bc9a9c306c53c0fb73e74b3c64e4, path rule/_index.yaml, selecting only entity=service.

Icon Registry is an identity consumer. It must not rename, merge, invent, or reinterpret Collection services.

## Invariants

- file stem == service_id;
- service_id exists in the pinned Collection snapshot;
- registry name == Collection display_name;
- registry provider == Collection provider;
- aggregate/category entries never count as canonical service coverage;
- shared image bytes do not imply shared service identity.

## Migration state

Phase A contract: complete.
Phase B pinned snapshot + report gate: complete.
Phase C registry normalization: in progress.
Phase D asset identity review: pending.
Phase E strict CI: blocked until C/D are clean.
