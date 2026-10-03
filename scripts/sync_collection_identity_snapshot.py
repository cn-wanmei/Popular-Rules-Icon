#!/usr/bin/env python3
"""sync_collection_identity_snapshot.py — Refresh Icon config/collection_identity_snapshot.json from Collection rule/_index.yaml.

Usage (Icon repo):
  python scripts/sync_collection_identity_snapshot.py
  python scripts/sync_collection_identity_snapshot.py --index-path /path/to/_index.yaml
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def load_index_text(path: Path | None, url: str | None) -> str:
    if path and path.is_file():
        return path.read_text(encoding="utf-8")
    if not url:
        raise SystemExit("need --index-path or --index-url")
    req = urllib.request.Request(url, headers={"User-Agent": "icon-snapshot-sync"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8")


def parse_service_ids(text: str) -> list[str]:
    ids: list[str] = []
    for m in re.finditer(
        r"entity:\s*service\s*\n(?:.*\n)*?\s*id:\s*['\"]?([A-Za-z0-9_.-]+)",
        text,
    ):
        ids.append(m.group(1))
    if not ids:
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("id:"):
                v = s.split(":", 1)[1].strip().strip("'\"")
                if v and not v.endswith("_aggregate"):
                    ids.append(v)
    seen = set()
    out = []
    for i in ids:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index-path", type=Path, default=None)
    ap.add_argument(
        "--index-url",
        default="https://raw.githubusercontent.com/cn-wanmei/Popular-Rules-Collection/main/rule/_index.yaml",
    )
    ap.add_argument("--out", type=Path, default=Path("config/collection_identity_snapshot.json"))
    args = ap.parse_args()

    text = load_index_text(args.index_path, args.index_url)
    services = parse_service_ids(text)
    payload = {
        "schema": "collection_identity_snapshot_v1",
        "source": "Popular-Rules-Collection/rule/_index.yaml",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "service_count": len(services),
        "services": services,
        "note": "Semi-auto sync; open PR after regenerate. Do not hand-edit service list.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {args.out} services={len(services)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
