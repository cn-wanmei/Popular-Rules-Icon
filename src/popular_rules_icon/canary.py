"""R1 canary: fetch official sources → state JSON + objects + PNG delivery variants."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import POLICY_VERSION, RENDERER_VERSION
from .acquire import fetch_url
from .hashutil import object_hash, source_fingerprint, variant_hash
from .render import make_source_original_png
from .sanitize import SanitizeError, sanitize_svg


def _parse_official_sources(path: Path) -> dict[str, list[dict[str, str]]]:
    text = path.read_text(encoding="utf-8")
    sources: dict[str, list[dict[str, str]]] = {}
    current: str | None = None
    for line in text.splitlines():
        m = re.match(r"^  ([a-z0-9_-]+):\s*$", line)
        if m:
            current = m.group(1)
            sources[current] = []
            continue
        if current and "url:" in line:
            um = re.search(r'url:\s*"([^"]+)"', line)
            cm = re.search(r"source_class:\s*([a-z0-9_]+)", line)
            if um:
                sources[current].append(
                    {
                        "url": um.group(1),
                        "source_class": cm.group(1) if cm else "official_page",
                    }
                )
    return sources


def _ext_for(data: bytes, content_type: str | None, is_svg: bool) -> str:
    if is_svg:
        return "svg"
    ct = (content_type or "").lower()
    if "jpeg" in ct or "jpg" in ct or data[:3] == b"\xff\xd8\xff":
        return "jpg"
    if "png" in ct or data[:8].startswith(b"\x89PNG"):
        return "png"
    if "webp" in ct or data[:4] == b"RIFF":
        return "webp"
    return "bin"


def acquire_canary(
    *,
    official_sources: Path,
    service_ids: list[str],
    out_state: Path,
    out_objects: Path | None = None,
    out_variants: Path | None = None,
) -> dict[str, Any]:
    table = _parse_official_sources(official_sources)
    out_state.mkdir(parents=True, exist_ok=True)
    if out_objects:
        out_objects.mkdir(parents=True, exist_ok=True)
    if out_variants:
        out_variants.mkdir(parents=True, exist_ok=True)

    summary: dict[str, Any] = {"ok": [], "failed": [], "entries": {}}
    now = datetime.now(timezone.utc).isoformat()

    for sid in service_ids:
        cands = table.get(sid) or []
        if not cands:
            summary["failed"].append({"service_id": sid, "code": "UNKNOWN", "error": "no candidates"})
            continue
        last_err = None
        for cand in cands:
            fr = fetch_url(cand["url"])
            if not fr.ok or not fr.data:
                last_err = {
                    "service_id": sid,
                    "code": fr.failure_code,
                    "error": fr.error,
                    "url": cand["url"],
                }
                continue
            data = fr.data
            source_class = cand["source_class"]
            is_svg = (
                (fr.content_type or "").lower().find("svg") >= 0
                or data[:200].lstrip().startswith(b"<svg")
                or data[:200].lstrip().startswith(b"<?xml")
            )
            try:
                if is_svg:
                    data = sanitize_svg(data)
            except SanitizeError as exc:
                last_err = {"service_id": sid, "code": exc.code, "error": str(exc)}
                continue

            oh = object_hash(data)
            fp = source_fingerprint(cand["url"], fr.etag, fr.last_modified, len(data))
            ext = _ext_for(data, fr.content_type, is_svg)
            if out_objects:
                (out_objects / f"{oh}.{ext}").write_bytes(data)

            variants: dict[str, str] = {}
            native_px = None
            try:
                for size in (128, 256):
                    vh, png, nat = make_source_original_png(
                        oh, data, size=size, max_upscale=1.0
                    )
                    native_px = nat
                    key = f"source_original:{size}:png"
                    variants[key] = vh
                    if out_variants:
                        (out_variants / f"{vh}.png").write_bytes(png)
            except Exception as exc:  # noqa: BLE001
                key = f"source_original:256:{ext}"
                vh = variant_hash(
                    oh,
                    renderer_version=RENDERER_VERSION,
                    style="source_original",
                    size=256,
                    fmt=ext,
                    policy_version=POLICY_VERSION,
                )
                variants[key] = vh
                if out_variants:
                    (out_variants / f"{vh}.{ext}").write_bytes(data)
                last_err = None
                # still success with fallback
                _ = exc

            state = {
                "service_id": sid,
                "source_fingerprint": fp,
                "object_hash": oh,
                "variant_hashes": variants,
                "source_class": source_class,
                "lifecycle": "active",
                "last_checked": now,
                "last_failure_code": None,
                "updated_at": now,
                "source_url": cand["url"],
                "native_px": native_px,
                "status": 200 if fr.status is None else fr.status,
            }
            (out_state / f"{sid}.json").write_text(
                json.dumps(state, indent=2) + "\n", encoding="utf-8"
            )
            summary["ok"].append(sid)
            summary["entries"][sid] = {
                "object_hash": oh,
                "variants": variants,
                "source_class": source_class,
                "native_px": native_px,
            }
            last_err = None
            break
        if last_err:
            summary["failed"].append(last_err)
            fail_state = {
                "service_id": sid,
                "source_fingerprint": None,
                "object_hash": None,
                "variant_hashes": {},
                "source_class": None,
                "lifecycle": "orphaned",
                "last_checked": now,
                "last_failure_code": last_err.get("code"),
                "updated_at": now,
            }
            (out_state / f"{sid}.json").write_text(
                json.dumps(fail_state, indent=2) + "\n", encoding="utf-8"
            )
    return summary
