"""Resolve service_id → content-addressed dist URL from physical manifest."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_manifest(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def resolve_service_id(
    service_id: str,
    *,
    registry_dir: str | Path | None = None,
) -> str:
    """R11: follow aliases / renamed_from in registry to canonical service_id."""
    if registry_dir is None:
        return service_id
    root = Path(registry_dir)
    if (root / f"{service_id}.json").exists():
        return service_id
    for p in root.glob("*.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        aliases = set(d.get("aliases") or [])
        renamed = set(d.get("renamed_from") or [])
        if service_id in aliases or service_id in renamed:
            return d.get("service_id") or p.stem
    return service_id


def variant_url(
    manifest: dict[str, Any],
    service_id: str,
    *,
    style: str = "source_original",
    size: int = 256,
    fmt: str = "png",
    mirror_template: str = "https://cdn.jsdelivr.net/gh/cn-wanmei/Popular-Rules-Icon@dist/v/{variant_hash}.png",
    registry_dir: str | Path | None = None,
) -> str | None:
    sid = resolve_service_id(service_id, registry_dir=registry_dir)
    key = f"{style}:{size}:{fmt}"
    for entry in manifest.get("entries") or []:
        if entry.get("service_id") != sid:
            continue
        variants = entry.get("variants") or {}
        meta = variants.get(key)
        if isinstance(meta, dict):
            vh = meta.get("variant_hash")
        else:
            vh = meta
        if not vh:
            return None
        return mirror_template.format(variant_hash=vh)
    return None
