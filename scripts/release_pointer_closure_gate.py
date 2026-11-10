#!/usr/bin/env python3
"""Audit production and rollback pointers against immutable dist manifests and files."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

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
EXPECTED_VARIANTS = {
    f"{style}:{size}:png" for style in STYLES for size in (128, 256)
}


def _audit_release(role: str, release_id: str, dist_root: Path, canonical_ids: set[str]) -> dict[str, Any]:
    errors: list[str] = []
    manifest_rel = Path("manifests") / f"{release_id}.json"
    manifest_path = dist_root / manifest_rel
    if not manifest_path.is_file():
        return {"role": role, "release_id": release_id, "manifest_path": manifest_rel.as_posix(),
                "status": "fail", "errors": [f"manifest missing: {manifest_rel.as_posix()}"]}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"role": role, "release_id": release_id, "manifest_path": manifest_rel.as_posix(),
                "status": "fail", "errors": [f"manifest unreadable: {exc}"]}

    if manifest.get("release_id") != release_id:
        errors.append(f"release_id mismatch: expected {release_id}, got {manifest.get('release_id')!r}")
    content_hash = str(manifest.get("content_hash") or "")
    if not HASH_RE.fullmatch(content_hash):
        errors.append("content_hash must be a 64-character lowercase SHA-256 hex string")
    if manifest.get("coverage_real") != 1:
        errors.append(f"coverage_real must be 1, got {manifest.get('coverage_real')!r}")
    if manifest.get("coverage_placeholder") != 0:
        errors.append(f"coverage_placeholder must be 0, got {manifest.get('coverage_placeholder')!r}")

    entries = manifest.get("entries")
    if not isinstance(entries, list):
        entries = []
        errors.append("manifest entries must be a list")
    ids = [str(entry.get("service_id") or "") for entry in entries if isinstance(entry, dict)]
    if len(ids) != len(entries):
        errors.append("manifest contains a non-object entry")
    if len(ids) != len(set(ids)):
        errors.append("manifest contains duplicate service IDs")
    missing_ids = sorted(canonical_ids - set(ids))
    orphan_ids = sorted(set(ids) - canonical_ids)
    if missing_ids:
        errors.append(f"canonical services missing: {missing_ids[:20]}")
    if orphan_ids:
        errors.append(f"orphan service IDs: {orphan_ids[:20]}")

    variant_records = 0
    unique_variants: set[str] = set()
    missing_paths: list[str] = []
    inactive_services: list[str] = []
    bad_variant_records: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        service_id = str(entry.get("service_id") or "<unknown>")
        if entry.get("status") != "active":
            inactive_services.append(service_id)
        variants = entry.get("variants") or {}
        if set(variants) != EXPECTED_VARIANTS:
            errors.append(f"{service_id}: expected {len(EXPECTED_VARIANTS)} variants, got {len(variants)}")
        for key, meta in variants.items():
            variant_records += 1
            if not isinstance(meta, dict):
                bad_variant_records.append(f"{service_id}:{key}: metadata is not an object")
                continue
            variant_hash = str(meta.get("variant_hash") or "")
            path = str(meta.get("path") or "")
            if not HASH_RE.fullmatch(variant_hash) or path != f"/v/{variant_hash}.png":
                bad_variant_records.append(f"{service_id}:{key}: invalid hash/path pair")
                continue
            relative = Path(path.lstrip("/"))
            if relative.is_absolute() or ".." in relative.parts or not relative.parts or relative.parts[0] != "v":
                bad_variant_records.append(f"{service_id}:{key}: unsafe path")
                continue
            target = dist_root / relative
            try:
                target.resolve().relative_to(dist_root.resolve())
            except ValueError:
                bad_variant_records.append(f"{service_id}:{key}: path escapes dist root")
                continue
            if not target.is_file() or target.stat().st_size <= 0:
                missing_paths.append(relative.as_posix())
            unique_variants.add(variant_hash)

    if inactive_services:
        errors.append(f"inactive services: {inactive_services[:20]}")
    if bad_variant_records:
        errors.append(f"bad variant records: {bad_variant_records[:20]}")
    if missing_paths:
        errors.append(f"missing/empty variant files: {missing_paths[:20]}")

    return {
        "role": role, "release_id": release_id, "manifest_path": manifest_rel.as_posix(),
        "content_hash": content_hash, "entries": len(entries), "canonical_services": len(canonical_ids),
        "variant_records": variant_records, "unique_variant_files": len(unique_variants),
        "missing_variant_files": len(missing_paths), "bad_variant_records": len(bad_variant_records),
        "inactive_services": len(inactive_services), "status": "pass" if not errors else "fail",
        "errors": errors,
    }


def audit_release_pointers(pointers_path: Path, snapshot_path: Path, dist_root: Path) -> dict[str, Any]:
    pointers = yaml.safe_load(pointers_path.read_text(encoding="utf-8")) or {}
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    canonical_ids = set((snapshot.get("services") or {}).keys())
    errors: list[str] = []
    if not canonical_ids:
        errors.append("Collection identity snapshot has no canonical services")
    production = str(pointers.get("production") or "").strip()
    rollback = str(pointers.get("rollback") or "").strip()
    if not production:
        errors.append("production pointer is missing")
    if not rollback:
        errors.append("rollback pointer is missing")
    if production and rollback and production == rollback:
        errors.append("production and rollback pointers must identify distinct releases")
    releases = []
    if production:
        releases.append(_audit_release("production", production, dist_root, canonical_ids))
    if rollback:
        releases.append(_audit_release("rollback", rollback, dist_root, canonical_ids))
    failed_roles = [item["role"] for item in releases if item["status"] != "pass"]
    return {
        "schema": "icon_release_pointer_closure_audit_v1",
        "status": "pass" if not errors and not failed_roles else "fail",
        "production": production, "rollback": rollback,
        "canonical_services": len(canonical_ids), "errors": errors, "releases": releases,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pointers", type=Path, default=Path("config/release-pointers.yaml"))
    parser.add_argument("--snapshot", type=Path, default=Path("config/collection_identity_snapshot.json"))
    parser.add_argument("--dist-root", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = audit_release_pointers(args.pointers, args.snapshot, args.dist_root)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
