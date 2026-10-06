# Full Icon Production Repair — 2026-10-06

## Scope

本次对当前 394 个 canonical services 全量从当前 seed/source 重建，强制丢弃旧 state 中的 object_hash / variant_hashes，确保 main 已完成的视觉源修正真正进入 production candidate。

## Service-specific source repair

共 50 个服务使用新的 service-specific source override。
优先来源：Simple Icons 维护的品牌 SVG；无对应图标时：官方服务域名 favicon。

## Explicit visual aliases

3 个关系保留共享视觉源：
epicgames -> epic, himalaya -> ximalaya, tencentdocs -> qqdoc

## Full rebuild

Release: icon-2026.10.06.full1
Canonical services: 394
Expected variants: 6304
State records forced to rebuild: 394

## Production promotion rule

只有 Identity Boundary、V6 Manifest、Production Icon Visual Identity、Style Policy、Physical Object Closure 全部通过后，才允许将 production pointer 切换到本 release。
