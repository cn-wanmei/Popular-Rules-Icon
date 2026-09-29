"""R1 canary: fetch official sources → state JSON + optional object bytes."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .acquire import fetch_url
from .hashutil import object_hash, source_fingerprint, variant_hash
from . import POLICY_VERSION, RENDERER_VERSION
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


def acquire_canary(
    *,
    official_sources: Path,
    service_ids: list[str],
    out_state: Path,
    out_objects: Path | None = None,
) -> dict[str, Any]:
    table = _parse_official_sources(official_sources)
    out_state.mkdir(parents=True, exist_ok=True)
    if out_objects:
        out_objects.mkdir(parents=True, exist_ok=True)
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
                last_err = {"service_id": sid, "code": fr.failure_code, "error": fr.error, "url": cand["url"]}
                continue
            data = fr.data
            source_class = cand["source_class"]
            # sanitize if svg
            is_svg = (fr.content_type or "").lower().find("svg") >= 0 or data[:200].lstrip().startswith(b"<svg") or data[:200].lstrip().startswith(b"<?xml")
            try:
                if is_svg:
                    data = sanitize_svg(data)
                    source_class = source_class if source_class.startswith("official") else "official_svg"
            except SanitizeError as exc:
                last_err = {"service_id": sid, "code": exc.code, "error": str(exc)}
                continue

            oh = object_hash(data)
            fp = source_fingerprint(cand["url"], fr.etag, fr.last_modified, len(data))
            vh = variant_hash(
                oh,
                renderer_version=RENDERER_VERSION,
                style="source_original",
                size=256,
                fmt="png" if not is_svg else "svg",
                policy_version=POLICY_VERSION,
            )
            if out_objects:
                ct = (fr.content_type or "").lower()
                if is_svg:
                    ext = "svg"
                elif "jpeg" in ct or "jpg" in ct or data[:3] == b"\xff\xd8\xff":
                    ext = "jpg"
                elif "png" in ct or data[:8] == b"\x89PNG\r\n\x1a\n":
                    ext = "png"
                elif "webp" in ct or data[:4] == b"RIFF":
                    ext = "webp"
                else:
                    ext = "bin"
                (out_objects / f"{oh}.{ext}").write_bytes(data)
            state = {
                "service_id": sid,
                "source_fingerprint": fp,
                "object_hash": oh,
                "variant_hashes": {f"source_original:256:{'svg' if is_svg else 'png'}": vh},
                "source_class": source_class,
                "lifecycle": "active",
                "last_checked": now,
                "last_failure_code": None,
                "updated_at": now,
                "source_url": cand["url"],
                "status": 200 if fr.status is None else fr.status,
            }
            (out_state / f"{sid}.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
            summary["ok"].append(sid)
            summary["entries"][sid] = {"object_hash": oh, "variant_hash": vh, "source_class": source_class}
            last_err = None
            break
        if last_err:
            summary["failed"].append(last_err)
            # still write failure state
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
            (out_state / f"{sid}.json").write_text(json.dumps(fail_state, indent=2) + "\n", encoding="utf-8")
    return summary
