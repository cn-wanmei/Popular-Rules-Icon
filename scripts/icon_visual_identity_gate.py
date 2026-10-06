#!/usr/bin/env python3
"""Audit production icon identity reuse and service-to-asset authorization.

This gate is deliberately narrower than a visual-computer-vision test:
it proves whether a production object is shared by multiple service IDs only
when the registry explicitly authorizes the relationship via icon_alias_of.
It also reports frozen-seed reliance and review debt so structural coverage
cannot be mistaken for visual identity quality.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

EXPECTED_STYLES = (
    "source_original",
    "glassmorphism",
    "soft_3d",
    "neo_skeuomorphism",
    "minimalist",
    "duotone_line",
    "mbe",
    "y2k",
)
EXPECTED_KEYS = {f"{style}:{size}:png" for style in EXPECTED_STYLES for size in (128, 256)}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_registry(path: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for p in sorted(path.glob("*.json")):
        data = load_json(p)
        sid = data.get("service_id") or p.stem
        out[str(sid)] = data
    return out


def alias_root(service_id: str, registry: dict[str, dict[str, Any]]) -> str:
    """Resolve icon_alias_of transitively; cycles/unknown targets stay visible."""
    seen: set[str] = set()
    cur = service_id
    while True:
        if cur in seen:
            return cur
        seen.add(cur)
        data = registry.get(cur) or {}
        target = data.get("icon_alias_of")
        if not isinstance(target, str) or not target:
            return cur
        cur = target


def duplicate_group_authorized(service_ids: list[str], registry: dict[str, dict[str, Any]]) -> bool:
    """Allow one canonical root + aliases, or aliases all pointing to one external root."""
    roots = {alias_root(sid, registry) for sid in service_ids}
    if len(roots) != 1:
        return False
    root = next(iter(roots))
    direct_root_present = root in service_ids
    for sid in service_ids:
        if sid == root and direct_root_present:
            continue
        data = registry.get(sid) or {}
        target = data.get("icon_alias_of")
        if not isinstance(target, str) or not target:
            return False
    return True


def audit(manifest: dict[str, Any], registry: dict[str, dict[str, Any]]) -> dict[str, Any]:
    entries = manifest.get("entries") or []
    by_object: dict[str, list[str]] = defaultdict(list)
    malformed: list[str] = []
    frozen_seed: list[str] = []
    review_debt: list[str] = []

    for entry in entries:
        sid = str(entry.get("service_id") or "")
        variants = entry.get("variants") or {}
        if set(variants) != EXPECTED_KEYS:
            malformed.append(sid)
        oh = entry.get("object_hash")
        if isinstance(oh, str) and oh:
            by_object[oh].append(sid)
        if entry.get("source_class") == "frozen_seed":
            frozen_seed.append(sid)
        if (registry.get(sid) or {}).get("review_status") == "needs_review":
            review_debt.append(sid)

    duplicate_groups = []
    unauthorized_groups = []
    for object_hash, service_ids in sorted(by_object.items(), key=lambda item: (-len(item[1]), item[0])):
        if len(service_ids) < 2:
            continue
        authorized = duplicate_group_authorized(service_ids, registry)
        rec = {
            "object_hash": object_hash,
            "count": len(service_ids),
            "service_ids": sorted(service_ids),
            "authorized_by_registry_alias": authorized,
            "alias_roots": sorted({alias_root(sid, registry) for sid in service_ids}),
        }
        duplicate_groups.append(rec)
        if not authorized:
            unauthorized_groups.append(rec)

    return {
        "schema": "icon_visual_identity_gate_v1",
        "release_id": manifest.get("release_id"),
        "generated_at": manifest.get("generated_at"),
        "entries": len(entries),
        "frozen_seed_entries": len(frozen_seed),
        "review_debt_entries": len(review_debt),
        "malformed_variant_entries": len(malformed),
        "duplicate_object_groups": len(duplicate_groups),
        "unauthorized_duplicate_object_groups": len(unauthorized_groups),
        "status": "pass" if not malformed and not unauthorized_groups else "drift",
        "malformed_service_ids": sorted(malformed),
        "review_debt_service_ids": sorted(review_debt),
        "duplicate_object_groups_detail": duplicate_groups,
        "unauthorized_duplicate_object_groups_detail": unauthorized_groups,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--registry", type=Path, default=Path("registry/services"))
    ap.add_argument("--write-report", type=Path)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    manifest = load_json(args.manifest)
    registry = load_registry(args.registry)
    report = audit(manifest, registry)
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(payload, end="")

    if args.write_report:
        args.write_report.parent.mkdir(parents=True, exist_ok=True)
        args.write_report.write_text(payload, encoding="utf-8")

    if args.strict and report["status"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
