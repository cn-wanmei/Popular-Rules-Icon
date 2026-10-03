#!/usr/bin/env python3
"""sync_collection_identity_snapshot.py — Refresh Icon config/collection_identity_snapshot.json
from Collection rule/_index.yaml at an **exact commit SHA** (not floating main).

Usage:
  python scripts/sync_collection_identity_snapshot.py
  python scripts/sync_collection_identity_snapshot.py --index-path /path/to/_index.yaml --commit-sha <sha>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_COMMIT = "https://api.github.com/repos/cn-wanmei/Popular-Rules-Collection/commits/main"
RAW_TMPL = "https://raw.githubusercontent.com/cn-wanmei/Popular-Rules-Collection/{ref}/rule/_index.yaml"


def http_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "icon-snapshot-sync", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def load_index_text(path: Path | None, url: str | None) -> tuple[str, bytes]:
    if path and path.is_file():
        raw = path.read_bytes()
        return raw.decode("utf-8"), raw
    if not url:
        raise SystemExit("need --index-path or remote url")
    req = urllib.request.Request(url, headers={"User-Agent": "icon-snapshot-sync"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read()
    return raw.decode("utf-8"), raw


def parse_entries(text: str) -> dict[str, dict]:
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
                "display_name": str(item.get("display_name") or sid),
                "provider": str(item.get("provider") or ""),
                "entity": "service",
            }
        return services

    raise SystemExit("Collection index has no entries[]")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index-path", type=Path, default=None)
    ap.add_argument("--commit-sha", default=None, help="Exact Collection commit; default resolve main HEAD")
    ap.add_argument("--out", type=Path, default=Path("config/collection_identity_snapshot.json"))
    args = ap.parse_args()

    commit_sha = (args.commit_sha or "").strip()
    if not commit_sha and not args.index_path:
        meta = http_json(API_COMMIT)
        commit_sha = str(meta.get("sha") or "")
        if len(commit_sha) < 40:
            raise SystemExit(f"could not resolve Collection main SHA: {commit_sha!r}")

    if args.index_path:
        text, raw = load_index_text(args.index_path, None)
        if not commit_sha:
            commit_sha = "local"
    else:
        url = RAW_TMPL.format(ref=commit_sha)
        text, raw = load_index_text(None, url)

    file_sha = hashlib.sha256(raw).hexdigest()
    services = parse_entries(text)
    if not services:
        raise SystemExit("parsed zero services from Collection index")

    prev: dict = {}
    if args.out.is_file():
        try:
            prev = json.loads(args.out.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            prev = {}

    payload = {
        "schema": prev.get("schema") or "collection_identity_snapshot_v1",
        "version": int(prev.get("version") or 1) + (0 if prev else 0),
        "source": {
            "repository": "cn-wanmei/Popular-Rules-Collection",
            "ref": commit_sha,
            "path": "rule/_index.yaml",
            "file_sha": file_sha,
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
        "note": "Pinned to exact Collection commit; do not hand-edit service map.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {args.out} services={len(services)} ref={commit_sha} file_sha={file_sha[:12]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
