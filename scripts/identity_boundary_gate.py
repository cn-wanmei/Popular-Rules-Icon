#!/usr/bin/env python3
"""Deterministic service identity boundary gate.

Canonical service identity comes from a pinned Popular-Rules-Collection snapshot.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, default=Path("config/collection_identity_snapshot.json"))
    ap.add_argument("--registry", type=Path, default=Path("registry/services"))
    ap.add_argument("--write-report", type=Path, default=None)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    snap = load_json(args.snapshot)
    if snap.get("schema") != "collection_icon_identity_snapshot_v1":
        raise SystemExit("unexpected snapshot schema")
    canonical = snap.get("services") or {}

    report = {
        "schema": "icon_identity_boundary_report_v1",
        "snapshot": snap.get("source"),
        "canonical_service_count": len(canonical),
        "registry_file_count": 0,
        "registry_service_count": 0,
        "missing_registry_records": [],
        "orphan_registry_records": [],
        "display_name_mismatches": [],
        "provider_mismatches": [],
        "file_id_mismatches": [],
        "invalid_registry_json": [],
        "duplicate_service_ids": [],
    }

    seen: set[str] = set()
    for path in sorted(args.registry.glob("*.json")):
        report["registry_file_count"] += 1
        try:
            item = load_json(path)
        except Exception as exc:
            report["invalid_registry_json"].append({"file": str(path), "error": str(exc)})
            continue

        sid = item.get("service_id")
        report["registry_service_count"] += 1
        if sid in seen:
            report["duplicate_service_ids"].append(sid)
        seen.add(sid)

        if sid != path.stem:
            report["file_id_mismatches"].append(
                {"file": str(path), "file_id": path.stem, "service_id": sid}
            )

        if sid not in canonical:
            report["orphan_registry_records"].append(
                {"service_id": sid, "name": item.get("name"), "provider": item.get("provider")}
            )
            continue

        expected = canonical[sid]
        if item.get("name") != expected.get("display_name"):
            report["display_name_mismatches"].append(
                {
                    "service_id": sid,
                    "icon_name": item.get("name"),
                    "canonical_name": expected.get("display_name"),
                }
            )
        if item.get("provider") != expected.get("provider"):
            report["provider_mismatches"].append(
                {
                    "service_id": sid,
                    "icon_provider": item.get("provider"),
                    "canonical_provider": expected.get("provider"),
                }
            )

    report["missing_registry_records"] = sorted(set(canonical) - seen)
    counts = {
        k: len(report[k])
        for k in (
            "missing_registry_records",
            "orphan_registry_records",
            "display_name_mismatches",
            "provider_mismatches",
            "file_id_mismatches",
            "invalid_registry_json",
            "duplicate_service_ids",
        )
    }
    report["counts"] = counts
    report["status"] = "pass" if not any(counts.values()) else "drift"

    encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(encoded, end="")
    if args.write_report:
        args.write_report.parent.mkdir(parents=True, exist_ok=True)
        args.write_report.write_text(encoded, encoding="utf-8")

    return 1 if args.strict and report["status"] != "pass" else 0


if __name__ == "__main__":
    raise SystemExit(main())
