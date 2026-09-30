# Service Identity Boundary — Icon Repository V1

## Authority

The canonical service identity is owned by:

- Repository: cn-wanmei/Popular-Rules-Collection
- Published index: rule/_index.yaml
- Selection: entity == service
- Pinned commit: 5bc537c894c88713f5a947dca91535318c610d23

The Icon repository is a consumer of this identity, not a second service catalog.

## Required invariant

For every file under registry/services:

1. file stem == service_id;
2. service_id exists in the pinned Collection service universe;
3. name exactly mirrors Collection display_name;
4. provider exactly mirrors Collection provider;
5. a service registry record must not correspond to a Collection aggregate/category;
6. a seed must exist for every production registry service.

## Important distinction

An icon asset may be visually shared by multiple service IDs without making those
service IDs equal.

Likewise, a product icon, parent-company icon, App Store result, or alias must not
rewrite the Collection service identity.

## Migration state

Phase A: contract defined in Collection.

Phase B: this repository now carries a deterministic Collection identity snapshot and
an executable identity-boundary gate.

Phase C: normalize registry metadata to the snapshot.

Phase D: review seed assets whose visual identity does not correspond to the canonical
service.

Phase E: enable strict CI so identity drift blocks release.

The current gate supports report-only operation during migration; strict mode is
intended after Phase C normalization.
