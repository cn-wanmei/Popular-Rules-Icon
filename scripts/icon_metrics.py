#!/usr/bin/env python3
"""R12 — Emit freeze metrics JSON."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

def main() -> int:
    ptr = {}
    p = Path("config/release-pointers.yaml")
    if p.exists():
        for line in p.read_text().splitlines():
            if ":" in line and not line.strip().startswith("#"):
                k, _, v = line.partition(":")
                ptr[k.strip()] = v.strip().strip('"')
    out = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "registry_services": len(list(Path("registry/services").glob("*.json"))),
        "seeds": len(list(Path("assets/icons/seed").glob("*"))),
        "objects": len(list(Path("assets/icons/objects").glob("*"))),
        "production": ptr.get("production"),
        "frozen": ptr.get("frozen"),
        "freeze_id": ptr.get("freeze_id"),
    }
    print(json.dumps(out, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
