#!/usr/bin/env python3
"""R9 — Dist GC: keep variants referenced by active physical manifests."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist-root", type=Path, required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = args.dist_root
    vdir, mdir = root / "v", root / "manifests"
    if not vdir.is_dir():
        print("no v/", file=sys.stderr)
        return 1
    keep: set[str] = set()
    for mf in mdir.glob("*.json"):
        data = json.loads(mf.read_text())
        for e in data.get("entries") or []:
            for h in (e.get("variants") or {}).values():
                if isinstance(h, str):
                    keep.add(h)
                elif isinstance(h, dict) and h.get("variant_hash"):
                    keep.add(h["variant_hash"])
    removed = []
    for f in vdir.iterdir():
        if f.is_file() and f.stem not in keep:
            removed.append(f.name)
            if not args.dry_run:
                f.unlink()
    print(json.dumps({"keep": len(keep), "removed": len(removed), "dry_run": args.dry_run}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
