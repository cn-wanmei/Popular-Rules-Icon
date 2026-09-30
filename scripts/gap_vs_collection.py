#!/usr/bin/env python3
"""R13 — Compare Icon registry to Collection service-id list (one id per line)."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--collection-ids", type=Path, required=True)
    ap.add_argument("--registry", type=Path, default=Path("registry/services"))
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()
    coll = {ln.strip() for ln in args.collection_ids.read_text().splitlines() if ln.strip() and not ln.startswith("#")}
    coll = {c for c in coll if not c.endswith("_aggregate") and c not in {"aggregate", "ai"}}
    reg = {p.stem for p in args.registry.glob("*.json")}
    missing = sorted(coll - reg)
    report = {
        "collection_ids": len(coll),
        "icon_registry": len(reg),
        "missing_in_icon": len(missing),
        "coverage_pct": round(100.0 * (len(coll) - len(missing)) / max(len(coll), 1), 2),
        "missing_sample": missing[:100],
    }
    text = json.dumps(report, indent=2, ensure_ascii=False)
    print(text)
    if args.json_out:
        args.json_out.write_text(text + "\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
