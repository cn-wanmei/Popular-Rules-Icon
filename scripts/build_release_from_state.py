#!/usr/bin/env python3
"""Fail-closed V6 release writer.

Reads an exact canonical state snapshot. Existing state records are reused.
A controlled seed bootstrap is supported for a missing canonical asset (currently AI)
and writes newly rendered variant objects to --objects-out.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from popular_rules_icon import POLICY_VERSION, RENDERER_VERSION
from popular_rules_icon.hashutil import object_hash, variant_hash
from popular_rules_icon.manifest import build_physical_manifest, write_manifest
from popular_rules_icon.pipeline import BuildResult
from popular_rules_icon.styles8 import render_all_styles

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
EXPECTED = {f"{style}:{size}:png" for style in STYLES for size in SIZES}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def materialize_seed(
    service_id: str,
    state: dict,
    *,
    seed_dir: Path,
    objects_out: Path,
    materialized_state_dir: Path,
) -> BuildResult:
    source_url = state.get("source_url", "")
    if not source_url.startswith("seed://"):
        raise ValueError(f"seed bootstrap requires seed:// source_url for {service_id}")
    filename = source_url.removeprefix("seed://")
    source = seed_dir / filename
    if not source.is_file():
        raise FileNotFoundError(f"seed asset missing: {source}")

    raw = source.read_bytes()
    if source.suffix.lower() == ".svg":
        import cairosvg

        source_png = cairosvg.svg2png(bytestring=raw, output_width=512, output_height=512)
    else:
        source_png = raw

    oh = object_hash(source_png)
    rendered = render_all_styles(source_png, sizes=SIZES)
    variant_hashes: dict[str, str] = {}
    objects_root = objects_out / "v"
    objects_root.mkdir(parents=True, exist_ok=True)

    for key, png in sorted(rendered.items()):
        style, size, fmt = key.split(":")
        vh = variant_hash(
            oh,
            renderer_version=RENDERER_VERSION,
            style=style,
            size=int(size),
            fmt=fmt,
            policy_version=POLICY_VERSION,
        )
        variant_hashes[key] = vh
        path = objects_root / f"{vh}.png"
        if path.exists() and path.read_bytes() != png:
            raise RuntimeError(f"variant hash collision with different bytes: {path}")
        path.write_bytes(png)

    if set(variant_hashes) != EXPECTED:
        raise RuntimeError(f"generated variant matrix incomplete for {service_id}")

    out_state = {
        **state,
        "service_id": service_id,
        "object_hash": oh,
        "variant_hashes": variant_hashes,
        "last_failure_code": None,
        "status": 200,
        "source_class": state.get("source_class", "original_generated"),
        "lifecycle": "active",
    }
    materialized_state_dir.mkdir(parents=True, exist_ok=True)
    (materialized_state_dir / f"{service_id}.json").write_text(
        json.dumps(out_state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return BuildResult(
        service_id=service_id,
        object_hash=oh,
        variant_hashes=variant_hashes,
        status="active",
        source_class=out_state["source_class"],
        failure_code=None,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state-dir", type=Path, required=True)
    ap.add_argument("--snapshot", type=Path, default=Path("config/collection_identity_snapshot.json"))
    ap.add_argument("--release-id", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seed-dir", type=Path, default=Path("assets/icons/seed"))
    ap.add_argument("--objects-out", type=Path, default=Path("build/objects"))
    ap.add_argument("--materialized-state-dir", type=Path, default=Path("build/materialized-state"))
    ap.add_argument("--allow-seed-bootstrap", action="store_true")
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

        variants = state.get("variant_hashes") or {}
        if state.get("object_hash") and set(variants) == EXPECTED:
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
            continue

        if not args.allow_seed_bootstrap:
            failures.append({
                "service_id": service_id,
                "code": "STATE_ASSET_MISSING",
                "missing_variants": sorted(EXPECTED - set(variants)),
            })
            continue

        try:
            result = materialize_seed(
                service_id,
                state,
                seed_dir=args.seed_dir,
                objects_out=args.objects_out,
                materialized_state_dir=args.materialized_state_dir,
            )
        except Exception as exc:
            failures.append({"service_id": service_id, "code": "SEED_BOOTSTRAP_FAILED", "error": str(exc)})
            continue
        results.append(result)
        seen.add(service_id)

    extra_state = sorted(
        p.stem for p in args.state_dir.glob("*.json") if p.stem not in canonical
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
        "generated_seed_objects": len(list((args.objects_out / "v").glob("*.png"))) if (args.objects_out / "v").exists() else 0,
        "out": str(args.out),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
