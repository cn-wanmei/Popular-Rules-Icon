# Icon Style System V1

**Status:** normative for Icon System 6.0 production keys  
**Does not change** manifest `style` identifiers.

Production styles are defined in `config/variant-policy.yaml` and materialised on branch `dist` as PNG objects addressed by content hash.

## Production style keys (immutable IDs)

| Key | 中文名 | English | Default resolver? | Typical use | Avoid |
|-----|--------|---------|-------------------|-------------|--------|
| `source_original` | 源图/品牌向 | Source original | **Yes (docs default)** | 识别优先、说明文档主图 | 强行当“设计系统唯一语言” |
| `minimalist` | 极简 | Minimalist | Optional | 列表、小尺寸、密集 UI | 需要强品牌色时 |
| `duotone_line` | 双色线稿 | Duotone line | Optional | 工具栏、线框感 | 需要填充品牌色时 |
| `soft_3d` | 柔和立体 | Soft 3D | Optional | 展示、卡片 | 极小尺寸可读性 |
| `glassmorphism` | 玻璃拟态 | Glassmorphism | Optional | 桌面/仪表盘 | 低对比背景 |
| `neo_skeuomorphism` | 新拟物 | Neo-skeuomorphism | Optional | 强调质感 | 扁平规范场景 |
| `mbe` | MBE 插画向 | MBE-style | Optional | 运营/展示 | 严肃企业列表 |
| `y2k` | Y2K | Y2K | No (experimental tone) | 实验/个性主题 | 默认生产 UI |

## Sizes & format

- Sizes: `128`, `256`
- Format: `png` only in production
- Object path: `/v/{variant_hash}.png` on `dist`

## Display name mapping (optional UI)

UI layers may show friendly labels; **must not** rewrite keys inside manifests.

```yaml
source_original: "Source / Brand"
minimalist: "Minimal"
duotone_line: "Duotone Line"
soft_3d: "Soft 3D"
glassmorphism: "Glass"
neo_skeuomorphism: "Neo-Skeuo"
mbe: "MBE"
y2k: "Y2K"
```

## Consumer defaults

- Collection docs (`config/icon_docs.yaml`): `source_original` + `256`
- Collection runtime: `config/icon_v6.yaml` → release id on `dist`

## Change policy

1. Adding a style = new variant-policy version + full release writer matrix + pointer bump.
2. Renaming a production key = **breaking**; require new release id and dual-read period.
3. Seed-only visual fixes require a new immutable release before clients see them (`frozen` production).
