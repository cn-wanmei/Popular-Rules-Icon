# Seed Visual Identity Audit — 2026-10-01

## Scope
Audited against the current canonical service universe from cn-wanmei/Popular-Rules-Collection rule/_index.yaml, entity: service.
Canonical services: 394
Canonical seed coverage before this pass: 394/394
Historical/orphan seed files: 89

Strict visual-identity rules:
1. The visible mark must identify the canonical service itself.
2. Parent-company, child-product, app-client, campaign, event, store, login, verification, or promotional artwork is not accepted as the parent/service mark unless that product is the canonical service.
3. A placeholder is not real coverage.
4. A visually shared asset never proves service identity equality.
5. When an exact externally sourced brand vector was available and could be fetched into the repository, it was used directly. No synthetic brand recreation was used.

## Confirmed wrong assets replaced in this pass
amd, appstore, cisco, dell, ea, hbo, lenovo, oppo, samsung, sap, sony, ubisoft, wegame, wise, qualcomm, rakuten, nintendo, oracle.

## Placeholder assets replaced in this pass
arm, fortinet, hitachi, intel, kakao, lg, mediatek, nokia, palantir, riotgames, roblox, shopee, siemens, snowflake, spacex, unity.

Total direct replacements: 34 canonical seeds.
The Nintendo and Oracle vectors were sourced from the Mibew/simple-icons `develop` mirror of Simple Icons; the mirror files explicitly identify the Nintendo and Oracle brand marks.
Exact vectors were sourced from Simple Icons 16.33.0. IconArchive's Simpleicons Team mirror identifies the same designer/brand pack and CC0 distribution metadata. Trademark rights remain with the respective owners.

## Confirmed wrong candidates still awaiting a repository-fetchable exact asset
安居客 (anjuke)
Anker (anker)
CCTV / 中国中央电视台 (cctv)
海康威视 / Hikvision (hikvision)
咪咕 (migu)
Microsoft Office (office)
Okta (okta)
PPTV (pptv)
Sohu / 搜狐 (sohu)
TSMC / 台积电 (tsmc)
Xbox (xbox)

## Canonical placeholder assets still awaiting exact assets
中国农业银行 / Agricultural Bank of China (abc)
ASML (asml)
Block (block)
Cadence (cadence)
Groq (groq)
Heroku (heroku)
HPE (hpe)
科大讯飞 (iflytek)
JD Cloud (jd-cloud)
京东云 (jdcloud)
金蝶 (kingdee)
KLA (kla)
昆仑芯 (kunlunxin)
Kuwo (kuwo)
Lam Research (lamresearch)
Lazada (lazada)
LeTV (letv)
满帮 (manbang)
Mercado Libre (mercadolibre)
Micron (micron)
Minecraft (minecraft)
NEC (nec)
NetApp (netapp)
NetEase Mail (neteasemail)
Palo Alto Networks (paloalto)
Panasonic (panasonic)
完美世界 (perfectworld)
平安科技 (pingan)
Private (private)
Postal Savings Bank of China (psbc)
360 (qihoo360)
去哪儿 (qunar)
Restricted (restricted)
石头科技 (roborock)
Rockstar Games (rockstar)
深信服 (sangfor)
Schneider Electric (schneider)
Google Scholar (scholar)
商汤科技 (sensetime)
世纪华通 (shiji)
石墨文档 (shimo)
SK hynix (skhynix)
Supermicro (supermicro)
Synopsys (synopsys)
T3出行 (t3go)
Take-Two (take2)
Temu (temu)
Texas Instruments (ti)
Tongcheng (tongcheng)
同花顺 (tonghuashun)
Toutiao (toutiao)
传音 (transsion)
UMC (umc)
唯品会 (vipshop)
火山引擎 (volcengine)
网宿科技 (wangsu)
完美世界 (wanmei)
WeCom (wecom)
WeTV (wetv)
Wikipedia (wikipedia)
Workday (workday)
联通云 (woyun)
58同城 (wuba)
Grok (xai-grok)
极米 (xgimi)
迅雷 (xunlei)
零一万物 (yi)
用友 (yonyou)
YouTube Music (youtubemusic)
智联招聘 (zhaopin)
BOSS直聘 (zhipin)
智谱AI (zhipu)
ZTE (zte)

## Special/generic service note
ai is canonical in Collection and has assets/icons/seed/ai.svg, but it is a neutral generated glyph rather than a service-specific corporate trademark. Under strict brand-identity semantics it remains unresolved as an exact brand asset.
private, restricted, and stun are generic/special identities; no invented trademark-like asset is allowed.

## Remaining visual-review queue
The previous risk review identified 94 current canonical candidates. 32 clearly wrong or placeholder assets have now been directly replaced. The remaining candidates are retained pending stronger evidence; visual similarity alone is not used to force replacement.

## Production impact
This branch changes seed-source identity only. It does not change the currently published clean1 V6 manifest until a new release is deliberately built and passed through the strict V6 manifest gate and physical-object closure.

## Source policy
Exact external assets used in this pass came from Simple Icons / Simpleicons Team vectors. For source items that could not be fetched into repository storage with sufficient fidelity/reliability, the existing seed is intentionally left untouched and the service is listed as unresolved.
