# Implementation Progress

| Phase | Status | Notes |
|-------|--------|-------|
| R0.1 | done | ADR freeze, archive, ADR-13..17 |
| R0.2 | done | schema/*, config/*, policies/* |
| R0.3 | done | registry 10 services, state branch |
| R0.4 | done | fixtures, pytest, pr-ci |
| R1 | **done** | acquire-canary: 10/10 ok; state branch updated |
| R2 | **done** | seeds in assets/icons/seed; registry lock=binding |
| R3 | **done** | dist branch icon-2026.09.29.1; production pointer set |
| R4 | **done** | Collection config/icon_v6.yaml (provider default v5) |
| R5 | pending | default cutover after shadow acceptance |
| R6+ | deferred | per Architecture Freeze |

## R1 canary result (2026-09-29)

All 10: github, google, apple, microsoft, openai, cloudflare, telegram, discord, wechat, alipay — acquired.

## Pointers

- Icon `state` branch: services/*.json
- Icon `dist` branch: v/, objects/, manifests/icon-2026.09.29.1.json
- Collection: config/icon_v6.yaml provider=v5 (shadow ready)
