#!/usr/bin/env python3
"""sync_collection_identity_snapshot.py — Refresh Icon config/collection_identity_snapshot.json
from Collection rule/_index.yaml (human_rule_distribution_index_v1 entries[]).

Usage (Icon repo):
  python scripts/sync_collection_identity_snapshot.py
  python scripts/sync_collection_identity_snapshot.py --index-path /path/to/_index.yaml
"""
from __future__ import annotations

import argparse
import json
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


def parse_entries(text: str) -> dict[str, dict]:
    """Return service_id -> minimal identity record from Collection index."""
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(f"PyYAML required: {exc}") from exc

    data = yaml.safe_load(text)
    services: dict[str, dict] = {}
    if not isinstance(data, dict):
        raise SystemExit(f"unexpected index root type: {type(data).__name__}")

    entries = data.get("entries")
    if isinstance(entries, list):
        for item in entries:
            if not isinstance(item, dict):
                continue
            ent = str(item.get("entity") or "service").lower()
            if ent != "service":
                continue
            sid = item.get("id") or item.get("service_id")
            if not sid:
                continue
            sid = str(sid)
            services[sid] = {
                "id": sid,
                "display_name": item.get("display_name") or sid,
                "provider": item.get("provider") or "",
                "entity": "service",
            }
        return services

    # Legacy fallbacks
    raw = data.get("services") or data.get("items") or {}
    if isinstance(raw, dict):
        for sid, meta in raw.items():
            if isinstance(meta, dict):
                ent = str(meta.get("entity") or meta.get("type") or "service").lower()
                if ent not in ("service", ""):
                    continue
            services[str(sid)] = {"id": str(sid), "entity": "service"}
    return services


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index-path", type=Path, default=None)
    ap.add_argument(
        "--index-url",
        default="https://raw.githubusercontent.com/cn-wanmei/Popular-Rules-Collection/main/rule/_index.yaml",
    )
    ap.add_argument("--out", type=Path, default=Path("config/collection_identity_snapshot.json"))
    args = ap.parse_args()

    text = load_index_text(args.index_path, args.index_url if not args.index_path else None)
    services = parse_entries(text)
    if not services:
        raise SystemExit("parsed zero services from Collection index")

    # Preserve prior envelope fields when present
    prev: dict = {}
    if args.out.is_file():
        try:
            prev = json.loads(args.out.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            prev = {}

    payload = {
        "schema": prev.get("schema") or "collection_identity_snapshot_v1",
        "version": prev.get("version") or 1,
        "source": {
            "repository": "cn-wanmei/Popular-Rules-Collection",
            "ref": "main",
            "path": "rule/_index.yaml",
            "selection": {
                "include_entity": "service",
                "exclude_entities": [
                    "provider_aggregate",
                    "aggregate",
                    "domestic_aggregate",
                    "category",
                ],
            },
        },
        "service_count": len(services),
        "services": services,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": "Auto/semi-auto sync from Collection entries[]; do not hand-edit service map.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {args.out} services={len(services)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
