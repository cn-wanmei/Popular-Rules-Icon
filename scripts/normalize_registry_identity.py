#!/usr/bin/env python3
"""Normalize Icon Registry identity fields against a pinned Collection snapshot.

Default mode is dry-run: writes a normalized staging tree and a report.
--apply updates only canonical registry records in place. Orphans are classified
but never deleted automatically.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, default=Path("config/collection_identity_snapshot.json"))
    ap.add_argument("--registry", type=Path, default=Path("registry/services"))
    ap.add_argument("--out", type=Path, default=Path("build/identity-normalized/registry/services"))
    ap.add_argument("--report", type=Path, default=Path("build/identity-normalization-report.json"))
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    snap = load(args.snapshot)
    canonical = snap.get("services") or {}
    entities = snap.get("entity_universe") or {}
    if not args.apply:
        args.out.mkdir(parents=True, exist_ok=True)

    report = {
        "schema": "icon_identity_normalization_report_v1",
        "canonical_service_count": len(canonical),
        "registry_file_count": 0,
        "canonical_records_normalized": 0,
        "already_canonical": 0,
        "orphan_provider_aggregate": [],
        "orphan_domestic_aggregate": [],
        "orphan_category": [],
        "orphan_unknown": [],
        "invalid_json": [],
        "apply_mode": args.apply,
    }

    for source in sorted(args.registry.glob("*.json")):
        report["registry_file_count"] += 1
        try:
            item = load(source)
        except Exception as exc:
            report["invalid_json"].append({"file": str(source), "error": str(exc)})
            continue

        sid = item.get("service_id") or source.stem

        if sid in canonical:
            expected = canonical[sid]
            old_name = item.get("name")
            old_provider = item.get("provider")
            item["service_id"] = sid
            item["name"] = expected.get("display_name")
            item["provider"] = expected.get("provider")
            item["identity_authority"] = "collection"
            item["identity_status"] = "canonical"
            if old_name == item["name"] and old_provider == item["provider"]:
                report["already_canonical"] += 1
            else:
                report["canonical_records_normalized"] += 1
        else:
            entity = entities.get(sid, {}).get("entity")
            record = {
                "service_id": sid,
                "name": item.get("name"),
                "provider": item.get("provider"),
            }
            if entity == "provider_aggregate":
                report["orphan_provider_aggregate"].append(record)
            elif entity == "domestic_aggregate":
                report["orphan_domestic_aggregate"].append(record)
            elif entity == "category":
                report["orphan_category"].append(record)
            else:
                report["orphan_unknown"].append(record)
            item["identity_authority"] = "collection"
            item["identity_status"] = "orphan"

        encoded = json.dumps(item, ensure_ascii=False, indent=2) + "\n"
        if args.apply and sid in canonical:
            source.write_text(encoded, encoding="utf-8")
        elif not args.apply:
            (args.out / source.name).write_text(encoded, encoding="utf-8")

    report["orphan_count"] = sum(
        len(report[k])
        for k in (
            "orphan_provider_aggregate",
            "orphan_domestic_aggregate",
            "orphan_category",
            "orphan_unknown",
        )
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
