#!/usr/bin/env python3
"""Fail closed on production pointer changes while an Icon V6 freeze is active."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


def _dt(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"{field} must include a timezone")
    return parsed


def _decision_errors(decision: Any, expected_type: str) -> list[str]:
    if not isinstance(decision, dict):
        return [f"freeze_decision.type={expected_type!r} with approval metadata is required"]
    errors = []
    if decision.get("type") != expected_type:
        errors.append(f"freeze_decision.type must be {expected_type!r}")
    for field in ("reason", "approved_by", "approved_at"):
        if not str(decision.get(field) or "").strip():
            errors.append(f"freeze_decision.{field} is required")
    if decision.get("approved_at"):
        try:
            _dt(decision["approved_at"], "freeze_decision.approved_at")
        except ValueError as exc:
            errors.append(str(exc))
    if expected_type == "unfreeze" and decision.get("rollback_verified") is not True:
        errors.append("freeze_decision.rollback_verified must be true before unfreeze")
    return errors


def evaluate_freeze_policy(
    base: dict[str, Any],
    candidate: dict[str, Any],
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now().astimezone()
    errors: list[str] = []
    base_frozen = base.get("frozen") is True
    candidate_frozen = candidate.get("frozen") is True
    production_changed = str(base.get("production") or "") != str(candidate.get("production") or "")
    freeze_fields = ("frozen", "freeze_id", "freeze_started_at", "freeze_expires_at", "max_freeze_days", "freeze_reason")
    freeze_changed = any(base.get(key) != candidate.get(key) for key in freeze_fields)
    decision = candidate.get("freeze_decision")

    if candidate_frozen:
        try:
            started = _dt(candidate.get("freeze_started_at"), "freeze_started_at")
            expires = _dt(candidate.get("freeze_expires_at"), "freeze_expires_at")
            max_days = int(candidate.get("max_freeze_days") or 0)
            if max_days <= 0:
                errors.append("max_freeze_days must be a positive integer")
            if expires <= started:
                errors.append("freeze_expires_at must be later than freeze_started_at")
            if max_days > 0 and (expires - started).total_seconds() > max_days * 86400:
                errors.append(f"freeze window exceeds max_freeze_days={max_days}")
            if expires <= now and (production_changed or freeze_changed):
                errors.append("freeze has expired; explicit unfreeze or extension decision is required")
        except (ValueError, TypeError) as exc:
            errors.append(str(exc))
        if not str(candidate.get("freeze_id") or "").strip():
            errors.append("freeze_id is required while frozen")
        if not str(candidate.get("freeze_reason") or "").strip():
            errors.append("freeze_reason is required while frozen")

    if production_changed and candidate_frozen:
        errors.append("production pointer changes are blocked while frozen=true")
    if production_changed and base_frozen and not candidate_frozen:
        errors.extend(_decision_errors(decision, "unfreeze"))

    if freeze_changed and base_frozen and candidate_frozen:
        if not isinstance(decision, dict) or decision.get("type") != "extension":
            errors.append("changing an active freeze requires freeze_decision.type='extension'")
        else:
            errors.extend(_decision_errors(decision, "extension"))
    if freeze_changed and not base_frozen and candidate_frozen:
        errors.extend(_decision_errors(decision, "start"))
    if base_frozen and not candidate_frozen and freeze_changed:
        errors.extend(_decision_errors(decision, "unfreeze"))

    return {
        "schema": "icon_freeze_policy_gate_v1",
        "status": "fail" if errors else "pass",
        "production_changed": production_changed,
        "base_frozen": base_frozen,
        "candidate_frozen": candidate_frozen,
        "base_production": base.get("production"),
        "candidate_production": candidate.get("production"),
        "freeze_id": candidate.get("freeze_id"),
        "freeze_expires_at": candidate.get("freeze_expires_at"),
        "errors": sorted(set(errors)),
    }


def evaluate_publish_policy(candidate: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now().astimezone()
    frozen = candidate.get("frozen") is True
    errors = []
    if frozen:
        raw_expiry = candidate.get("freeze_expires_at")
        if raw_expiry:
            try:
                expires = _dt(raw_expiry, "freeze_expires_at")
                if expires <= now:
                    errors.append("publish blocked: freeze has expired without an explicit decision")
                else:
                    errors.append("publish blocked: V6 production freeze is still active")
            except ValueError as exc:
                errors.append(str(exc))
        else:
            errors.append("publish blocked: frozen=true without freeze_expires_at")
    return {
        "schema": "icon_freeze_publish_gate_v1",
        "status": "fail" if errors else "pass",
        "frozen": frozen,
        "freeze_id": candidate.get("freeze_id"),
        "freeze_expires_at": candidate.get("freeze_expires_at"),
        "errors": errors,
    }


def _read_base(ref: str, path: str) -> dict[str, Any]:
    raw = subprocess.check_output(["git", "show", f"{ref}:{path}"], text=True)
    return yaml.safe_load(raw) or {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-ref")
    parser.add_argument("--candidate", type=Path, default=Path("config/release-pointers.yaml"))
    parser.add_argument("--base-path", default="config/release-pointers.yaml")
    parser.add_argument("--require-unfrozen", action="store_true")
    args = parser.parse_args()
    candidate = yaml.safe_load(args.candidate.read_text(encoding="utf-8")) or {}
    if args.require_unfrozen:
        report = evaluate_publish_policy(candidate)
    else:
        if not args.base_ref:
            parser.error("--base-ref is required unless --require-unfrozen is set")
        base = _read_base(args.base_ref, args.base_path)
        report = evaluate_freeze_policy(base, candidate)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
