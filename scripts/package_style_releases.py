#!/usr/bin/env python3
"""package_style_releases.py — Build 8 style icon zip artifacts + release notes.

V6 variant keys (from production manifests):
  source_original, glassmorphism, soft_3d, neo_skeuomorphism,
  minimalist, duotone_line, mbe, y2k

Each style packs both 128 and 256 png variants when present.
Zip naming: {style-slug}-{release_id}.zip
"""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# (manifest_variant_prefix, zip_slug, display_title)
STYLES: list[tuple[str, str, str]] = [
    ("source_original", "source-original", "Source Original"),
    ("glassmorphism", "glassmorphism", "Glassmorphism"),
    ("soft_3d", "soft-3d-claymorphism", "Soft 3D / Claymorphism"),
    ("neo_skeuomorphism", "neo-skeuomorphism", "Neo-Skeuomorphism"),
    ("minimalist", "minimalist-glyph-multicolor-flat", "Minimalist Glyph & Multi-color Flat"),
    ("duotone_line", "two-tone-broken-line", "Two-tone / Broken Line"),
    ("mbe", "mbe-illustration", "MBE Illustration"),
    ("y2k", "y2k-synthwave", "Y2K / Synthwave"),
]


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _resolve_local(rel: str, search_roots: list[Path]) -> Path | None:
    rel = rel.lstrip("/")
    for root in search_roots:
        p = root / rel
        if p.is_file():
            return p
        # also try without leading v/
        if rel.startswith("v/"):
            p2 = root / rel[2:]
            if p2.is_file():
                return p2
        p3 = root / "v" / Path(rel).name
        if p3.is_file():
            return p3
    return None


def _collect_variant_paths(
    manifest: dict[str, Any],
    style_prefix: str,
    search_roots: list[Path],
) -> list[tuple[str, Path]]:
    results: list[tuple[str, Path]] = []
    for entry in manifest.get("entries") or []:
        service_id = entry.get("service_id") or entry.get("id") or "unknown"
        variants = entry.get("variants") or {}
        for key, meta in variants.items():
            if not str(key).startswith(style_prefix + ":"):
                continue
            if not isinstance(meta, dict):
                continue
            rel = (meta.get("path") or "").lstrip("/")
            if not rel:
                continue
            local = _resolve_local(rel, search_roots)
            if local is None:
                continue
            # arc: service_id / size / filename
            size = "256" if ":256:" in str(key) else "128" if ":128:" in str(key) else "unknown"
            arc = f"{service_id}/{size}/{local.name}"
            results.append((arc, local))
    return results


def _zip_paths(pairs: list[tuple[str, Path]], dest: Path) -> int:
    count = 0
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for arc, src in sorted(pairs, key=lambda x: x[0]):
            zf.write(src, arc)
            count += 1
    return count


def build_notes(
    *,
    release_id: str,
    style_stats: dict[str, dict[str, Any]],
    total_icons: int,
    prev_release: str | None,
    added: list[str],
    deleted: list[str],
    modified: list[str],
) -> str:
    lines: list[str] = []
    lines.append(f"# Popular-Rules-Icon Release Notes — {release_id}")
    lines.append("")
    lines.append("## 总览")
    lines.append("")
    lines.append(f"- **Release ID**: `{release_id}`")
    lines.append(f"- **风格数**: **8**")
    lines.append(f"- **图标文件合计（本包）**: **{total_icons}**")
    if prev_release:
        lines.append(f"- **对比基线**: `{prev_release}`")
    lines.append("")
    lines.append("## 八风格发行包")
    lines.append("")
    lines.append("| 风格 | 文件名 | 图标数 |")
    lines.append("|---|---|---:|")
    for _prefix, slug, title in STYLES:
        st = style_stats.get(slug, {})
        lines.append(f"| {title} | `{st.get('zip_name', '')}` | {st.get('icon_count', 0)} |")
    lines.append("")
    lines.append("## 本次变更（相对上一 production）")
    lines.append("")
    lines.append(f"- **新增图标 (service)**: {len(added)}")
    if added:
        for s in added[:50]:
            lines.append(f"  - `{s}`")
        if len(added) > 50:
            lines.append(f"  - … 另有 {len(added) - 50} 项")
    lines.append(f"- **删除图标 (service)**: {len(deleted)}")
    if deleted:
        for s in deleted[:50]:
            lines.append(f"  - `{s}`")
        if len(deleted) > 50:
            lines.append(f"  - … 另有 {len(deleted) - 50} 项")
    lines.append(f"- **修改图标 (service)**: {len(modified)}")
    if modified:
        for s in modified[:50]:
            lines.append(f"  - `{s}`")
        if len(modified) > 50:
            lines.append(f"  - … 另有 {len(modified) - 50} 项")
    lines.append("")
    lines.append("---")
    lines.append("*本说明由 `scripts/package_style_releases.py` 自动生成。*")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--release-id", required=True)
    parser.add_argument("--out-dir", type=Path, default=Path("release-packages"))
    parser.add_argument("--prev-manifest", type=Path, default=None)
    parser.add_argument("--prev-release-id", default="")
    parser.add_argument(
        "--objects-root",
        type=Path,
        action="append",
        default=[],
        help="Root(s) to search for physical png objects (repeatable)",
    )
    args = parser.parse_args()

    manifest = _load_json(args.manifest)
    if not manifest:
        raise SystemExit(f"cannot load manifest: {args.manifest}")

    search_roots = list(args.objects_root) if args.objects_root else [
        Path("build/objects"),
        Path("build/v"),
        Path("."),
    ]

    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    cur_ids = set()
    for e in manifest.get("entries") or []:
        sid = e.get("service_id") or e.get("id")
        if sid:
            cur_ids.add(sid)

    prev_ids: set[str] = set()
    prev_hashes: dict[str, str] = {}
    if args.prev_manifest and args.prev_manifest.is_file():
        prev = _load_json(args.prev_manifest) or {}
        for e in prev.get("entries") or []:
            sid = e.get("service_id") or e.get("id")
            if not sid:
                continue
            prev_ids.add(sid)
            variants = e.get("variants") or {}
            digests = []
            for v in variants.values():
                if isinstance(v, dict) and (v.get("variant_hash") or v.get("sha256")):
                    digests.append(v.get("variant_hash") or v.get("sha256"))
            if digests:
                prev_hashes[sid] = "|".join(sorted(digests))

    added = sorted(cur_ids - prev_ids) if prev_ids else []
    deleted = sorted(prev_ids - cur_ids) if prev_ids else []
    modified: list[str] = []
    if prev_hashes:
        for e in manifest.get("entries") or []:
            sid = e.get("service_id") or e.get("id")
            if not sid or sid not in prev_hashes:
                continue
            variants = e.get("variants") or {}
            digests = []
            for v in variants.values():
                if isinstance(v, dict) and (v.get("variant_hash") or v.get("sha256")):
                    digests.append(v.get("variant_hash") or v.get("sha256"))
            cur_h = "|".join(sorted(digests)) if digests else ""
            if cur_h and cur_h != prev_hashes.get(sid):
                modified.append(sid)
        modified = sorted(modified)

    style_stats: dict[str, dict[str, Any]] = {}
    total_icons = 0

    for prefix, slug, _title in STYLES:
        pairs = _collect_variant_paths(manifest, prefix, search_roots)
        zip_name = f"{slug}-{args.release_id}.zip"
        dest = out / zip_name
        count = _zip_paths(pairs, dest) if pairs else 0
        if not pairs:
            with zipfile.ZipFile(dest, "w") as zf:
                zf.writestr(
                    "README.txt",
                    f"No physical assets resolved for style {prefix} in this run.\n"
                    f"Search roots: {[str(r) for r in search_roots]}\n",
                )
            count = 0
        total_icons += count
        style_stats[slug] = {
            "zip_name": zip_name,
            "icon_count": count,
            "sha256": _sha256_file(dest),
            "size_bytes": dest.stat().st_size,
            "variant_prefix": prefix,
        }
        print(f"[package] {zip_name} icons={count}")

    notes = build_notes(
        release_id=args.release_id,
        style_stats=style_stats,
        total_icons=total_icons,
        prev_release=args.prev_release_id or None,
        added=added,
        deleted=deleted,
        modified=modified,
    )
    notes_path = out / "RELEASE_NOTES.md"
    notes_path.write_text(notes, encoding="utf-8")

    sums_path = out / "SHA256SUMS.txt"
    with sums_path.open("w", encoding="utf-8") as f:
        for _p, slug, _t in STYLES:
            st = style_stats[slug]
            f.write(f"{st['sha256']}  {st['zip_name']}\n")
        f.write(f"{_sha256_file(notes_path)}  RELEASE_NOTES.md\n")

    meta = {
        "schema": "icon_style_release_package_v1",
        "release_id": args.release_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "styles": style_stats,
        "total_icons": total_icons,
        "added": added,
        "deleted": deleted,
        "modified": modified,
        "zip_count": 8,
    }
    (out / "release-meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"[package] wrote 8 style zips + RELEASE_NOTES.md")
    print(f"[package] added={len(added)} deleted={len(deleted)} modified={len(modified)}")
    if total_icons == 0:
        print("[package] WARNING: zero icons resolved — check objects roots")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
