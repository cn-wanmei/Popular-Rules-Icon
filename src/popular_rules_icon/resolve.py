"""Resolve service_id → content-addressed dist URL from physical manifest."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_manifest(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def variant_url(
    manifest: dict[str, Any],
    service_id: str,
    *,
    style: str = "source_original",
    size: int = 256,
    fmt: str = "png",
    mirror_template: str = "https://cdn.jsdelivr.net/gh/cn-wanmei/Popular-Rules-Icon@dist/v/{variant_hash}.png",
) -> str | None:
    key = f"{style}:{size}:{fmt}"
    for entry in manifest.get("entries") or []:
        if entry.get("service_id") != service_id:
            continue
        variants = entry.get("variants") or {}
        # variants may be {key: {variant_hash, path}} or {key: hash}
        meta = variants.get(key)
        if isinstance(meta, dict):
            vh = meta.get("variant_hash")
        else:
            vh = meta
        if not vh:
            return None
        return mirror_template.format(variant_hash=vh)
    return None
