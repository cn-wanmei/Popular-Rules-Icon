# Popular Rules Icon

<p align="center">
  <img src="https://img.shields.io/badge/System-Icon%20V6-6366f1?style=for-the-badge" alt="V6" />
  <img src="https://img.shields.io/badge/Dist-content--addressed-0d9488?style=for-the-badge" alt="Content-addressed" />
  <img src="https://img.shields.io/badge/Identity-Collection%20SSOT-1e293b?style=for-the-badge" alt="Identity" />
  <img src="https://img.shields.io/badge/Release-manual%20packages-64748b?style=for-the-badge" alt="Manual" />
</p>

<p align="center">
  <strong>Icon System 6.0 · Variant · Immutable Dist · Production Pointer</strong><br/>
  <sub>Asset layer for Popular-Rules-Collection canonical services</sub>
</p>

---

## 定位

**Popular Rules Icon** 为 Collection 的 canonical `service_id` 提供 **Icon System 6.0** 资产。

本仓库负责：

- Icon variant / Style system
- Content-addressed objects
- Immutable release manifest
- Production pointer / Rollback pointer
- Icon distribution

> **服务身份不在本仓库定义。**

---

## 身份边界

```text
Popular-Rules-Collection
        ↓
canonical service_id
display_name
provider
        ↓
Popular-Rules-Icon
        ↓
icon asset binding
```

| 内容 | 权威入口 |
|------|----------|
| Service Identity | [Collection `rule/_index.yaml`](https://github.com/cn-wanmei/Popular-Rules-Collection/blob/main/rule/_index.yaml) |
| Identity Snapshot | [`config/collection_identity_snapshot.json`](config/collection_identity_snapshot.json) |
| Production Release | [`config/release-pointers.yaml`](config/release-pointers.yaml) |
| Rollback Release | [`config/release-pointers.yaml`](config/release-pointers.yaml) |
| Style Semantics | [`config/variant-policy.yaml`](config/variant-policy.yaml) |
| Style Display | [`config/style-display.yaml`](config/style-display.yaml) |
| Distribution Objects | [`dist/`](https://github.com/cn-wanmei/Popular-Rules-Icon/tree/dist) |

Icon Registry **消费** Collection identity，但**不反向定义** Collection service。

## Coverage 口径（勿与 Collection 全条目数混淆）

Icon **只**绑定 Collection `rule/_index.yaml` 中 `entity: service` 的条目。

- `provider_aggregate` / `aggregate` / `category` **不在** Icon 覆盖范围内。
- 因此 `release-pointers.yaml` 中 `100% (394/394)` 表示 **全部 service** 已绑定，**不是**相对 `_index` 总 entries（常 ~651）的缺口。
- 正式合同：[`docs/COVERAGE_AND_FRESHNESS.md`](docs/COVERAGE_AND_FRESHNESS.md)


---

## Style System

| Style | 语义 |
|-------|------|
| `source_original` | 原始来源风格 |
| `minimalist` | 线稿极简 |
| `duotone_line` | 双色线 |
| `soft_3d` | 柔和立体 |
| `glassmorphism` | 玻璃态 |
| `neo_skeuomorphism` | 新拟物 |
| `mbe` | MBE |
| `y2k` | Y2K |

- Style policy：[`config/variant-policy.yaml`](config/variant-policy.yaml)
- Style display：[`config/style-display.yaml`](config/style-display.yaml)

---

## Content-addressed distribution

生产对象使用：

```text
dist/v/<sha256>.png
```

对象由内容寻址。同一个内容对应同一个 object identity。  
Release manifest 与 production pointer **不覆盖**历史 immutable object。

---

## 生产链

```text
Collection Identity
        ↓
Pinned Identity Snapshot
        ↓
Icon Build
        ↓
Release Writer
        ↓
Strict Gates
        ↓
Immutable dist
        ↓
Production Pointer
        ↓
Collection Resolver
```

---

## Release / Rollback

生产与回滚均由 [`config/release-pointers.yaml`](config/release-pointers.yaml) 统一描述。

```text
production
    ↓
rollback
```

首页**不手写**：

- 当前 Release ID
- 回滚 Release ID
- 服务数量 / Variant 数量 / Coverage 百分比

这些值全部从生产指针与 Registry 读取。

---

## 当前状态

| 状态域 | 权威入口 |
|--------|----------|
| Production release | [`config/release-pointers.yaml`](config/release-pointers.yaml) |
| Rollback release | [`config/release-pointers.yaml`](config/release-pointers.yaml) |
| Collection identity | [`config/collection_identity_snapshot.json`](config/collection_identity_snapshot.json) |
| Variant policy | [`config/variant-policy.yaml`](config/variant-policy.yaml) |
| Production manifest | `dist/` |
| Production branches | `main` / `dist` / `state` |

身份快照同步：`scripts/sync_collection_identity_snapshot.py` → 开 PR，**勿手改**服务列表。

---

## 快速入口

| 用途 | 入口 |
|------|------|
| 生产指针 | [`config/release-pointers.yaml`](config/release-pointers.yaml) |
| Collection 身份快照 | [`config/collection_identity_snapshot.json`](config/collection_identity_snapshot.json) |
| Style Policy | [`config/variant-policy.yaml`](config/variant-policy.yaml) |
| Style Display | [`config/style-display.yaml`](config/style-display.yaml) |
| Gallery | [`docs/gallery/INDEX.md`](docs/gallery/INDEX.md) |
| GitHub Releases | [Releases](https://github.com/cn-wanmei/Popular-Rules-Icon/releases) |

---

## Consumer

Collection 文档层 / 服务页可直接引用 content-addressed object：

```html
<img
  src="https://raw.githubusercontent.com/cn-wanmei/Popular-Rules-Icon/dist/v/<sha256>.png"
  alt="service icon"
  width="72"
  height="72">
```

---

## Release

Icon **生产 Release** 与 **用户 GitHub Release** 分离：

| 阶段 | 作用 |
|------|------|
| V6 Release Writer | 生成 immutable production release |
| Production Pointer | 指向当前生产版本 |
| Rollback Pointer | 指向独立回滚版本 |
| Icon Style GitHub Release Packages | 用户发行包；仅 **手动** `workflow_dispatch` |

> Release Writer 成功**不会**自动创建用户 GitHub Release。

---

## 文档

| 文档 | 用途 |
|------|------|
| [`docs/INDEX.md`](docs/INDEX.md) | 文档索引 |
| [`docs/IDENTITY_BOUNDARY_V1.md`](docs/IDENTITY_BOUNDARY_V1.md) | Identity Boundary |
| [`docs/PRODUCTION_IDENTITY_AUDIT_2026-09-30.md`](docs/PRODUCTION_IDENTITY_AUDIT_2026-09-30.md) | Production identity audit |
| [`docs/STYLE_SYSTEM_V1.md`](docs/STYLE_SYSTEM_V1.md) | Style semantics |
| [`docs/gallery/INDEX.md`](docs/gallery/INDEX.md) | 生产预览 |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | 贡献规范 |

---

## 关联项目仓库

| 仓库 | 关系 |
|------|------|
| [Popular-Rules-Collection](https://github.com/cn-wanmei/Popular-Rules-Collection) | Canonical Service Identity 与最终规则消费方 |
| [Popular-Rules-Source](https://github.com/cn-wanmei/Popular-Rules-Source) | Evidence Supply Layer；通过 Collection 间接关联，不定义 Icon identity |

```text
Popular-Rules-Source
        │
        │ Evidence
        ▼
Popular-Rules-Collection
        │
        │ Canonical Identity
        ▼
Popular-Rules-Icon
        │
        │ Icon Assets
        ▼
Collection Documentation / Consumer
```

---

<sub>README 描述制度与入口；动态数字与覆盖率以各仓 SSOT / CI 生成为准。</sub>
