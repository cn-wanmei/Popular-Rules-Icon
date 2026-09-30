#!/usr/bin/env python3
"""Validate an Icon V6 immutable manifest against the Collection identity snapshot."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HASH_RE = re.compile(r"^[0-9a-f]{64}$")
STYLES = (
    "source_original",
    "glassmorphism",
    "soft_3d",
    "neo_skeuomorphism",
    "minimalist",
    "duotone_line",
    "mbe",
    "y2k",
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--snapshot", type=Path, default=Path("config/collection_identity_snapshot.json"))
    ap.add_argument("--release-id", required=True)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
    canonical = set((snapshot.get("services") or {}).keys())

    problems: list[str] = []
    if manifest.get("release_id") != args.release_id:
        problems.append(f"release_id mismatch: expected {args.release_id!r}, got {manifest.get('release_id')!r}")

    entries = manifest.get("entries") or []
    ids = [e.get("service_id") for e in entries]
    if len(ids) != len(set(ids)):
        problems.append("duplicate service_id in manifest")

    manifest_ids = set(ids)
    missing = sorted(canonical - manifest_ids)
    orphan = sorted(manifest_ids - canonical)

    bad_paths = 0
    bad_variants = 0
    for entry in entries:
        variants = entry.get("variants") or {}
        expected = {f"{style}:{size}:png" for style in STYLES for size in (128, 256)}
        if set(variants) != expected:
            bad_variants += 1
            continue
        for meta in variants.values():
            if not isinstance(meta, dict):
                bad_variants += 1
                continue
            path = meta.get("path", "")
            vh = meta.get("variant_hash", "")
            if not isinstance(path, str) or not path.startswith("/v/") or not path.endswith(".png"):
                bad_paths += 1
            if not isinstance(vh, str) or not HASH_RE.fullmatch(vh):
                bad_variants += 1

    result = {
        "schema": "icon_v6_manifest_gate_report_v1",
        "release_id": manifest.get("release_id"),
        "entries": len(entries),
        "canonical_collection_services": len(canonical),
        "canonical_present": len(canonical & manifest_ids),
        "missing_canonical": len(missing),
        "orphan_entries": len(orphan),
        "bad_paths": bad_paths,
        "bad_variant_records": bad_variants,
        "missing_service_ids": missing,
        "orphan_service_ids": orphan,
        "status": "pass" if not (problems or missing or orphan or bad_paths or bad_variants) else "drift",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.strict and result["status"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
