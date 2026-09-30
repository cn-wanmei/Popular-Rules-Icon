# Seed Visual Identity Audit — 2026-10-01

## Scope
Current Collection main defines 394 canonical entries with entity=service. The Icon seed tree contains the 394 canonical seeds plus 89 historical/orphan seed files.

Strict rule: the visible mark must identify the canonical service itself. Product/client/store/campaign/verification/promotion artwork is rejected for a parent/service identity unless that product is the canonical service. Placeholder is not real coverage. No synthetic trademark recreation is used.

## Direct replacements completed

Total: 34 canonical seed assets.

Confirmed wrong assets replaced:
- amd
- appstore
- cisco
- dell
- ea
- hbo
- lenovo
- oppo
- samsung
- sap
- sony
- ubisoft
- wegame
- wise
- qualcomm
- rakuten
- nintendo
- oracle

Former placeholder assets replaced with exact brand vectors:
- arm
- fortinet
- hitachi
- intel
- kakao
- lg
- mediatek
- nokia
- palantir
- riotgames
- roblox
- shopee
- siemens
- snowflake
- spacex
- unity

Source families: Simple Icons 16.33.0 for the first group and Mibew/simple-icons develop mirror for Nintendo/Oracle. The Simpleicons Team IconArchive mirror documents the brand pack as CC0/public-domain and identifies the designer. Trademark ownership remains with the respective brand owners.

## Confirmed wrong assets still unresolved
These are visually confirmed mismatches, but this pass did not obtain a repository-writeable exact vector/raster asset with sufficient source fidelity:
- anjuke
- anker
- cctv
- hikvision
- ibm
- migu
- office
- okta
- pptv
- sohu
- tsmc
- xbox

## Canonical placeholder assets still unresolved
These remain placeholder-only in the current audit record because an exact repository-writeable brand asset was not obtained:
- abc
- asml
- block
- cadence
- groq
- heroku
- hpe
- iflytek
- jd-cloud
- jdcloud
- kingdee
- kla
- kunlunxin
- kuwo
- lamresearch
- lazada
- letv
- manbang
- mercadolibre
- micron
- minecraft
- nec
- netapp
- neteasemail
- paloalto
- panasonic
- perfectworld
- pingan
- private
- psbc
- qihoo360
- qunar
- restricted
- roborock
- rockstar
- sangfor
- schneider
- scholar
- sensetime
- shiji
- shimo
- skhynix
- supermicro
- synopsys
- t3go
- take2
- temu
- ti
- tongcheng
- tonghuashun
- toutiao
- transsion
- umc
- venmo
- vipshop
- volcengine
- wangsu
- wanmei
- wecom
- wetv
- wikipedia
- workday
- woyun
- wuba
- xai-grok
- xgimi
- xunlei
- yi
- yonyou
- youtubemusic
- zhaopin
- zhipin
- zhipu
- zte

## Generic/special identities
- ai: canonical Collection service; current seed is a neutral generated glyph, not a service-specific corporate mark.
- private, restricted, stun: generic/special identities; do not invent trademark-like assets.

## Current seed status after this pass
- canonical service identities: 394
- direct visual replacements: 34
- confirmed-wrong unresolved: 12
- placeholder unresolved: 74
- historical/orphan seed files: 89

## Production impact
This branch changes seed inputs and source pointers only. It does not alter the already-published clean1 V6 manifest. A new immutable release must be built and pass the strict V6 manifest and physical-object closure gates before these seed changes become production output.

## Evidence boundary
The current pass exhaustively reviewed the repository's existing high-risk/placeholder queues and directly replaced every queue item for which an exact source asset was successfully acquired into repository storage. Assets not meeting that evidence standard were left untouched and listed above rather than guessed.
