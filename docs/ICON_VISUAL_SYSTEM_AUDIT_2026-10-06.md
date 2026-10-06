# Popular-Rules-Icon 图标系统严格审计报告

**审计日期：** 2026-10-06  
**目标仓库：** `cn-wanmei/Popular-Rules-Icon`  
**当前生产指针：** `icon-2026.09.30.clean1`  
**当前生产 manifest：** 394 services × 8 styles × 2 sizes = 6,304 variant records

## 一、执行结论

本次审计将系统拆成四层分别验证：

1. **服务身份是否正确**：Collection canonical service → pinned identity snapshot → registry.
2. **源图身份是否正确**：official source / seed → state object → production manifest.
3. **渲染是否完整**：8 styles × 128/256 PNG 的矩阵、hash、dist object closure。
4. **样式是否适用**：服务品牌识别优先，装饰性样式只能是派生变体，不能反向成为身份事实。

当前仓库对第 1、2、3 层已有较完整的内容寻址和 fail-closed 基础，但**第 4 层几乎没有自动化约束，第 2 层也缺少“跨 service 共用同一 object 必须显式授权”的生产级硬闸门**。

因此：

> `394/394 + 16 variants/service + 0 placeholder` 只能证明“结构覆盖完整”，不能证明“图标与服务身份匹配”。

当前 clean1 生产包是在 2026-09-30 生成的，而已合并到 main 的服务视觉身份修正发生在 2026-10-01；这些 seed 修正没有进入当前冻结的 clean1 production manifest。也就是说，**当前 production 与当前 main seed 事实已经发生视觉资产代际漂移**。

## 二、当前完整工作流程

### 1. Canonical service authority

唯一服务身份权威来自：

`Popular-Rules-Collection/rule/_index.yaml`

Icon 仓库通过 `config/collection_identity_snapshot.json` 固定 service_id / display_name / provider。

### 2. Identity boundary

`config/identity-boundary.yaml` 声明：

- registry 不是身份权威；
- service_id 必须存在于 canonical snapshot；
- registry name/provider 必须与 canonical identity 一致；
- aggregate/category 不计为 service；
- shared visual asset 不允许天然合并 service_id；
- production registry 必须存在 seed；
- 当前为 strict 模式。

这是正确的架构方向。

### 3. Registry layer

`registry/services/*.json` 保存服务级元数据，包括：

- service_id
- name
- provider
- asset_class
- aliases / renamed_from
- icon_alias_of
- review_status
- lock

其中 `icon_alias_of` 是目前唯一明确的“允许共享视觉身份”的表达方式。

### 4. Source / seed layer

生产源图主要来自：

`assets/icons/seed/*`

当前 seed 树共有 **483 个文件 / 399 个唯一 Git blob / 36 组重复 blob**。

这说明当前 seed 层存在大量“不同 service_id → 完全相同源图”的情况；其中部分是合法品牌家族/别名，但目前没有统一的自动化证据闸门强制它必须由 `icon_alias_of` 解释。

### 5. Acquisition / sanitization

`src/popular_rules_icon/acquire.py`

负责远端抓取、SSRF 防护、大小限制、ETag/Last-Modified。

`sanitize.py`

负责 SVG 安全解析，拦截 script / javascript URI / foreignobject / iframe / object / embed / event attributes 等。

### 6. Canary / state

`canary.py`

负责：

source candidate → fetch/local seed → sanitize → object_hash → source_fingerprint → render 8 styles → variant_hash → state JSON。

生产 clean1 最终并没有重新抓官方源，而是直接复用了已有 state 中的 object_hash + variant_hashes。

### 7. Rendering

`styles8.py`

当前一次源图派生出 8 种视觉风格：

- source_original
- glassmorphism
- soft_3d
- neo_skeuomorphism
- minimalist
- duotone_line
- mbe
- y2k

全部基于同一 raster source 做 Pillow 后处理。

这里的关键问题是：**当前渲染器是“统一效果器”，不是“service-aware style engine”**。

没有服务级的：

- style allowlist
- style denylist
- brand-color preservation rule
- wordmark protection
- high-detail logo protection
- experimental-style opt-in
- small-size readability gate

因此“有 8 个变体”不等于“8 个变体都适合这个服务”。

### 8. State → immutable release

`scripts/build_release_from_state.py`

生产发布默认直接复用 state 中已有的 16 个变体。

只有显式 `--allow-seed-bootstrap` 才会重新从 seed 构造 source/object/variants。

当前 release workflow 没有打开该 bootstrap，因此：

> seed 改了 ≠ production 自动更新。

这正是本次发现 clean1 与 main seed 发生漂移的根本原因之一。

### 9. V6 manifest gate

当前 `v6_manifest_gate.py` 可以检查：

- release_id
- duplicate service_id
- canonical missing
- orphan
- 16 variant records
- /v/<hash>.png 路径
- 64hex variant hash

但是原 gate **不检查 service_id → visual object 的身份授权**，也不检查 style 适用性。

### 10. Dist

发布到 `dist` 后：

`/v/{variant_hash}.png`

通过内容寻址保证 immutable。

### 11. Production pointer

当前：

`config/release-pointers.yaml`

指向：

`production: icon-2026.09.30.clean1`

并且：

- 394/394 canonical
- 0 orphan
- 0 placeholder
- 8 styles

生产冻结至 2026-11-14。

### 12. Consumer resolver

`resolve.py`

完成：

service_id → alias/rename resolution → manifest variant → jsDelivr content-addressed URL。

这里也没有视觉适用性判断。

## 三、当前生产包实测结构

当前 clean1 manifest：

- services：394
- coverage_real：100%
- placeholder：0
- 每 service：16 variants
- 每 style：394 services
- source_class：**393 frozen_seed + 1 original_generated**
- failure：0
- duplicate object groups：**21**

其中“393 frozen_seed”是非常重要的生产质量信号：

> 当前所谓 clean production 并不是 393 个服务实时重新拿官方 source 构建，而是绝大多数直接从冻结 seed state 复用。

这在 immutable 发布机制上是合法的，但在视觉身份质量上必须依赖“seed 审计 + state 重建”闭环。

## 四、当前生产已确认的视觉身份错配

clean1 生成之后，main 在 2026-10-01 合并了一整轮视觉身份修正。根据已合并的 seed 修正提交，以下 **42 个服务**的 source asset 已被主线判定为视觉身份错误/不匹配并完成 seed 侧替换，但这些修正尚未回灌当前 clean1 production：

### 第一批

amd、appstore、cisco、dell  
ea、hbo、lenovo、oppo  
qualcomm、rakuten、wegame、wise

### Google 系列

google-chat、google-docs、google-forms、google-meet  
google-earth、google-news、google-photos、google-sheets、google-slides  
google-play、googlecloud

### 其他已修正

huggingface、jetbrains、supermicro、wikipedia、woocommerce  
ericsson、fujitsu、paloalto、rockstar  
alipay、broadcom、cloudflare、docker、firebase、google-calendar

**结论：这些不能被算作“当前 production 已修复”。它们只在 main seed 层已修复。**

## 五、当前 production 仍确认未解决的错配

历史严格视觉审计还明确记录了以下 12 个服务仍为视觉身份错配、当时没有拿到可可靠写入仓库的精确品牌资产：

anjuke、anker、cctv、hikvision、ibm、migu、office、okta、pptv、sohu、tsmc、xbox

因此这些服务目前仍属于 P1/P2 视觉资产 backlog。

## 六、当前 production 的 21 组共享 object 风险

clean1 实际存在以下共享 object group：

- firebase + 大量 Google 服务
- copilot + Microsoft 365/Office/SharePoint
- honorofkings_cn/global + 多个腾讯/QQ 服务
- Apple 多个产品服务 + appstore
- aisuite + Anthropic/Claude
- Adobe Firefly/Fonts/Stock
- Facebook/Messenger/Threads
- Find My/iCloud/Private Relay
- Xiaomi GetApps/Mi Cloud/Mi Home
- OpenAI/OpenAI API/OpenAI Platform
- 1688/Fliggy
- AMap/Gaode
- Epic/Epic Games
- HeyTap/OPPO
- Himalaya/Ximalaya
- Huawei AppGallery/Huawei Cloud
- Hugging Face/Perplexity
- Microsoft Edge/Power BI
- SAP/Snapchat
- Stripe/Stripe Dashboard
- Ubisoft/Xbox

其中一部分已经有 `icon_alias_of` 明确授权，例如 OpenAI API → OpenAI、Stripe Dashboard → Stripe、Find My → iCloud、Messenger/Threads → Meta、Google 产品 → Google、Adobe 产品 → Adobe。

但以下共享组属于**高风险身份错配**，不能继续依赖“文件碰巧一样”：

- firebase
- copilot
- aisuite
- perplexity / huggingface
- snapchat / sap
- xbox / ubisoft
- fliggy / 1688
- heytap / oppo

另外腾讯、Apple、Xiaomi、Huawei、Microsoft 365 产品簇也必须继续逐项验证，不能用 provider 相同替代产品身份相同。

## 七、样式系统本身发现的问题

Normative Style System 已经把：

- source_original 定义为默认品牌/识别基线；
- y2k 定义为实验性风格，并明确写出“避免默认生产 UI”。

但当前 `config/icon-demand.yaml` 仍把 **y2k 放在 defaults 和 rich 默认需求**中。

这是制度自身的不一致。

本次已把默认 demand 收紧为非实验风格，并将 y2k 定义为 explicit opt-in experimental style。

同时新增：

`config/style-compatibility.yaml`

明确：

- source_original = identity baseline / required
- minimalist / duotone_line / soft_3d / glassmorphism / neo_skeuomorphism = supported
- mbe = supported_opt_in
- y2k = experimental / explicit demand only

注意：这不会删除 dist 中的 8-style immutable objects，只修正“默认需求语义”。

## 八、真正的根因

### 根因 A：结构门禁 ≠ 身份门禁

原 V6 gate 只验证：

`service_id × variant matrix × path × hash`

没有验证：

`service_id × object_hash × icon_alias_of`

因此错误图标完全可以在：

394/394、16/16、0 failure

的情况下成功发布。

### 根因 B：seed 修复没有自动推动 state rebuild

main seed 修复后：

`seed changed → state unchanged → clean1 unchanged`

当前体系没有自动把这条链闭合。

### 根因 C：style renderer 没有 service-aware compatibility

8 个样式是统一效果器，不是服务感知的视觉策略。

### 根因 D：生产冻结导致“当前 main 已修正 / current production 未修正”长期并存

这是 immutable 的正常副作用，但没有配套的 “seed-change → state rebuild → candidate → release → pointer promotion” 强制审计，因此非常容易被“100% coverage”掩盖。

## 九、本次执行的工程改进

已建立审计分支：

`audit/icon-visual-system-20261006`

已加入：

`scripts/icon_visual_identity_gate.py`

其职责：

- 扫描生产 manifest
- 扫描 registry/services
- 按 object_hash 找跨 service 共享源对象
- 解析 icon_alias_of 链
- 只有 registry 明确授权的共享视觉资产才视为合法
- 输出 unauthorized duplicate object groups
- 同时报告 frozen_seed 和 review debt
- 可使用 `--strict` 作为发布硬闸门

同时新增：

`config/style-compatibility.yaml`

并收紧默认 demand，不再把 Y2K 当作默认生产需求。

## 十、尚未贸然自动替换的部分

本次没有把“provider 相同”“产品属于同一家公司”“文件 hash 一样”直接当作合法别名。

这是必须保持的原则。

例如：

- Google 产品之间可以有品牌家族关系，但 Google Search / Google Earth / Google Photos 不应仅凭 provider=google 自动判定“视觉相同就是正确”；
- Microsoft Office / Copilot / Edge / Power BI 同理；
- Apple / App Store / TestFlight / Find My 同理。

必须由：

`icon_alias_of + 证据 + 明确服务身份`

共同证明。

## 十一、最终质量判定

### Identity

**未达生产 clean 标准。**

因为当前 clean1 仍包含已被 main 视觉审计判定错误、但尚未重新 release 的资产。

### Structural

**通过。**

394/394、16 variants/service、content-addressed dist 均完整。

### Style

**部分通过。**

8-style 生产链完整，但 service-aware style compatibility 尚未完整建立。

### Governance

**需要加强。**

main 当前 branch protection 为关闭状态；production pointer 冻结虽然安全，但缺少强制的“视觉资产变更必须重新生成 state/release”的自动链路。

## 十二、下一阶段正确生产闭环

正确闭环必须固定为：

**Collection canonical identity**
→ **pinned identity snapshot**
→ **service visual audit**
→ **exact source / seed**
→ **state rebuild**
→ **object + 8×2 variants**
→ **identity visual gate**
→ **V6 manifest gate**
→ **physical object closure**
→ **immutable dist release**
→ **reviewed production pointer promotion**

不能再使用：

**main seed 已修复 → 直接认为 production 已修复。**

## 审计证据

- PR #14：严格服务身份视觉审计与 seed replacement
- 2026-10-01 多个 `fix(seed): ... visual mismatches` 提交
- clean1 manifest：2026-09-30 生成
- current main：2026-10-05 更新
- current state branch：2026-09-30
- 当前 manifest：21 组 duplicate object
