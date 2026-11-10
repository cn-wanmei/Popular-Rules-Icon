#!/usr/bin/env python3
"""Calculate the next freeze-expiry reminder for the scheduled GitHub workflow."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def freeze_alert(pointers: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    if pointers.get("frozen") is not True:
        return {"alert": "none", "freeze_id": pointers.get("freeze_id"), "days_left": None}
    raw = str(pointers.get("freeze_expires_at") or "").strip()
    if not raw:
        raise ValueError("freeze_expires_at is required while frozen")
    expires = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if expires.tzinfo is None:
        raise ValueError("freeze_expires_at must include a timezone")
    seconds = (expires - now).total_seconds()
    if seconds <= 0:
        alert = "expired"
    elif seconds <= 86400:
        alert = "24h"
    elif seconds <= 3 * 86400:
        alert = "3d"
    elif seconds <= 7 * 86400:
        alert = "7d"
    else:
        alert = "none"
    return {
        "alert": alert,
        "freeze_id": str(pointers.get("freeze_id") or "unknown"),
        "freeze_expires_at": expires.isoformat(),
        "days_left": round(seconds / 86400, 2),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pointers", type=Path, default=Path("config/release-pointers.yaml"))
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    pointers = yaml.safe_load(args.pointers.read_text(encoding="utf-8")) or {}
    report = freeze_alert(pointers)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.github_output:
        marker = f"<!-- freeze-expiry:{report.get('freeze_id')}:{report['alert']} -->"
        with args.github_output.open("a", encoding="utf-8") as output:
            for key, value in report.items():
                output.write(f"{key}={value if value is not None else ''}\n")
            output.write(f"marker={marker}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
