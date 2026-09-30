#!/usr/bin/env python3
"""Validate Popular-Rules-Icon identity against a pinned Collection snapshot."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_snapshot(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "collection_icon_identity_snapshot_v1":
        raise ValueError(f"unexpected snapshot schema: {data.get('schema')!r}")
    if data.get("version") != 1:
        raise ValueError(f"unexpected snapshot version: {data.get('version')!r}")
    services = data.get("services")
    if not isinstance(services, dict):
        raise ValueError("snapshot.services must be an object")
    return data


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, default=Path("config/collection_identity_snapshot.json"))
    ap.add_argument("--registry", type=Path, default=Path("registry/services"))
    ap.add_argument("--seed", type=Path, default=Path("assets/icons/seed"))
    ap.add_argument("--write-report", type=Path, default=None)
    ap.add_argument("--strict", action="store_true", help="exit 1 when identity drift exists")
    args = ap.parse_args()

    snapshot = load_snapshot(args.snapshot)
    canonical = snapshot["services"]
    registry_files = sorted(args.registry.glob("*.json"))

    report = {
        "schema": "icon_identity_boundary_report_v1",
        "snapshot": {
            "repository": snapshot["source"]["repository"],
            "ref": snapshot["source"]["ref"],
            "path": snapshot["source"]["path"],
            "service_count": snapshot["service_count"],
        },
        "registry_file_count": len(registry_files),
        "registry_service_count": 0,
        "canonical_service_count": len(canonical),
        "missing_registry_records": [],
        "orphan_registry_records": [],
        "display_name_mismatches": [],
        "provider_mismatches": [],
        "file_id_mismatches": [],
        "invalid_registry_json": [],
        "duplicate_registry_service_ids": [],
        "seed_missing_for_registry": [],
    }

    seen = set()
    for path in registry_files:
        try:
            item = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            report["invalid_registry_json"].append({"file": str(path), "error": str(exc)})
            continue

        service_id = item.get("service_id")
        stem_id = path.stem
        if service_id != stem_id:
            report["file_id_mismatches"].append(
                {"file": str(path), "file_id": stem_id, "service_id": service_id}
            )

        if service_id in seen:
            report["duplicate_registry_service_ids"].append(service_id)
        seen.add(service_id)
        report["registry_service_count"] += 1

        if service_id not in canonical:
            report["orphan_registry_records"].append(
                {"service_id": service_id, "name": item.get("name"), "provider": item.get("provider")}
            )
            continue

        expected = canonical[service_id]
        if item.get("name") != expected.get("display_name"):
            report["display_name_mismatches"].append(
                {
                    "service_id": service_id,
                    "icon_name": item.get("name"),
                    "canonical_name": expected.get("display_name"),
                }
            )

        if item.get("provider") != expected.get("provider"):
            report["provider_mismatches"].append(
                {
                    "service_id": service_id,
                    "icon_provider": item.get("provider"),
                    "canonical_provider": expected.get("provider"),
                }
            )

        seed_candidates = list(args.seed.glob(service_id + ".*"))
        if not seed_candidates:
            report["seed_missing_for_registry"].append(service_id)

    report["missing_registry_records"] = sorted(set(canonical) - seen)

    counts = {
        "missing": len(report["missing_registry_records"]),
        "orphans": len(report["orphan_registry_records"]),
        "display_name_mismatches": len(report["display_name_mismatches"]),
        "provider_mismatches": len(report["provider_mismatches"]),
        "file_id_mismatches": len(report["file_id_mismatches"]),
        "invalid_json": len(report["invalid_registry_json"]),
        "duplicate_service_ids": len(report["duplicate_registry_service_ids"]),
        "seed_missing_for_registry": len(report["seed_missing_for_registry"]),
    }
    report["counts"] = counts
    report["status"] = "pass" if not any(counts.values()) else "drift"

    encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(encoded, end="")
    if args.write_report:
        args.write_report.parent.mkdir(parents=True, exist_ok=True)
        args.write_report.write_text(encoded, encoding="utf-8")

    if args.strict and report["status"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
