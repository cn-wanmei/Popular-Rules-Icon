# Popular-Rules-Icon

> Icon System **6.0** — independent, incremental, content-addressed, immutable-manifest icon infrastructure for the Popular-Rules ecosystem.

## Architecture Freeze

**Baseline:** [`docs/ADR-Freeze-Rev.3.1.md`](docs/ADR-Freeze-Rev.3.1.md)

Do **not** implement abolished designs (see freeze doc). Legacy planning files live under [`docs/archive/`](docs/archive/).

## Status

| Phase | Status |
|-------|--------|
| R0.1 Documentation freeze | landed |
| R0.2 Schema | landed |
| R0.3 Registry samples + state layout | landed |
| R0.4 Fixtures + L0/L1 CI | landed |
| R1 Network acquire (canary) | library SSRF/sanitize ready; full net canary incremental |
| R2 Score / lock / curated seeds | score + lock helpers landed |
| R3 dist + release pointers | config + workflow placeholders |
| R4–R5 Collection shadow / cutover | pending Collection integration |

## Layout

```text
schema/     JSON contracts
config/     default_demand, score_rules, release-pointers
policies/   versioned policy YAML (ADR-14)
registry/   human-reviewed service facts
src/        Python core
tests/      L0–L1 fixtures (synthetic geometry, no brand logos)
```

## Surfaces

| Surface | Role |
|---------|------|
| `main` | code, schema, registry, policies |
| `state` branch | bot fingerprints (sharded JSON) |
| `dist` | `/v/{variant_hash}` artifacts (R3) |

## Quick start

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m popular_rules_icon.cli fixture-run --svg tests/fixtures/geom_blue.svg
```

## License

Code: MIT (`LICENSE`). Brand icons: see `NOTICE` — not granted under MIT.
