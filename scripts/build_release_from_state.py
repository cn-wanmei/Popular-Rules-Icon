#!/usr/bin/env python3
"""Fail-closed release manifest writer from an exact Icon state snapshot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from popular_rules_icon.manifest import build_physical_manifest, write_manifest
from popular_rules_icon.pipeline import BuildResult

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
SIZES = (128, 256)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state-dir", type=Path, required=True)
    ap.add_argument("--snapshot", type=Path, default=Path("config/collection_identity_snapshot.json"))
    ap.add_argument("--release-id", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    snapshot = load_json(args.snapshot)
    canonical = set((snapshot.get("services") or {}).keys())
    if not canonical:
        raise SystemExit("canonical service snapshot is empty")

    results: list[BuildResult] = []
    seen: set[str] = set()
    failures: list[dict] = []

    for service_id in sorted(canonical):
        path = args.state_dir / f"{service_id}.json"
        if not path.is_file():
            failures.append({"service_id": service_id, "code": "STATE_MISSING"})
            continue

        try:
            state = load_json(path)
        except Exception as exc:
            failures.append({"service_id": service_id, "code": "STATE_INVALID_JSON", "error": str(exc)})
            continue

        if state.get("service_id") != service_id:
            failures.append({"service_id": service_id, "code": "STATE_ID_MISMATCH"})
            continue
        if state.get("lifecycle", "active") != "active":
            failures.append({"service_id": service_id, "code": "STATE_NOT_ACTIVE", "lifecycle": state.get("lifecycle")})
            continue
        if not state.get("object_hash"):
            failures.append({"service_id": service_id, "code": "OBJECT_MISSING"})
            continue

        variants = state.get("variant_hashes") or {}
        expected = {f"{style}:{size}:png" for style in STYLES for size in SIZES}
        if set(variants) != expected:
            failures.append({
                "service_id": service_id,
                "code": "VARIANT_MATRIX_INCOMPLETE",
                "missing": sorted(expected - set(variants)),
                "extra": sorted(set(variants) - expected),
            })
            continue

        results.append(
            BuildResult(
                service_id=service_id,
                object_hash=state["object_hash"],
                variant_hashes=variants,
                status="active",
                source_class=state.get("source_class"),
                failure_code=state.get("last_failure_code"),
            )
        )
        seen.add(service_id)

    extra_state = sorted(
        p.stem
        for p in args.state_dir.glob("*.json")
        if p.stem not in canonical
    )

    if extra_state:
        failures.append({"code": "STATE_ORPHANS_PRESENT", "service_ids": extra_state})

    if failures or seen != canonical:
        print(json.dumps({
            "status": "blocked",
            "release_id": args.release_id,
            "canonical_services": len(canonical),
            "ready_services": len(seen),
            "failures": failures,
        }, ensure_ascii=False, indent=2))
        return 2

    manifest = build_physical_manifest(
        args.release_id,
        results,
        policy_snapshot="policies/render-policy-v1.yaml",
    )
    manifest["release_writer"] = "scripts/build_release_from_state.py"
    manifest["source_snapshot"] = snapshot.get("source")
    write_manifest(str(args.out), manifest)

    print(json.dumps({
        "status": "ready",
        "release_id": manifest["release_id"],
        "canonical_services": len(results),
        "variants_per_service": 16,
        "content_hash": manifest["content_hash"],
        "out": str(args.out),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
