#!/usr/bin/env python3
"""R10 — Fail if registry service lacks seed file."""
from __future__ import annotations
import argparse, sys
from pathlib import Path

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, default=Path("registry/services"))
    ap.add_argument("--seed", type=Path, default=Path("assets/icons/seed"))
    args = ap.parse_args()
    fails = []
    for p in sorted(args.registry.glob("*.json")):
        sid = p.stem
        if not list(args.seed.glob(f"{sid}.*")):
            fails.append(f"{sid}: missing seed")
    if fails:
        print("FREEZE COVERAGE GATE FAILED", len(fails))
        for f in fails[:50]:
            print(" ", f)
        return 1
    print("FREEZE COVERAGE GATE PASS", len(list(args.registry.glob('*.json'))))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
