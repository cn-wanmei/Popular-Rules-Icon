from __future__ import annotations

from datetime import datetime, timezone

from scripts.freeze_policy_gate import evaluate_freeze_policy
from scripts.freeze_expiry_monitor import freeze_alert


NOW = datetime(2026, 11, 10, 12, 0, tzinfo=timezone.utc)
BASE = {
    "production": "icon-old",
    "rollback": "icon-rb",
    "frozen": True,
    "freeze_id": "freeze-1",
    "freeze_started_at": "2026-10-06T19:21:00+08:00",
    "freeze_expires_at": "2026-11-20T19:21:00+08:00",
    "max_freeze_days": 45,
    "freeze_reason": "production repair",
}


def test_pointer_gate_passes_when_production_pointer_is_unchanged() -> None:
    report = evaluate_freeze_policy(BASE, dict(BASE), NOW)
    assert report["status"] == "pass"


def test_pointer_gate_blocks_production_change_while_frozen() -> None:
    candidate = {**BASE, "production": "icon-new"}
    report = evaluate_freeze_policy(BASE, candidate, NOW)
    assert report["status"] == "fail"
    assert any("blocked while frozen" in item for item in report["errors"])


def test_pointer_gate_allows_production_change_after_audited_unfreeze() -> None:
    candidate = {
        **BASE,
        "production": "icon-new",
        "frozen": False,
        "freeze_decision": {
            "type": "unfreeze",
            "reason": "all release and rollback gates passed",
            "approved_by": "maintainer",
            "approved_at": "2026-11-19T10:00:00Z",
            "rollback_verified": True,
        },
    }
    report = evaluate_freeze_policy(BASE, candidate, NOW)
    assert report["status"] == "pass"


def test_pointer_gate_rejects_unfreeze_without_rollback_verification() -> None:
    candidate = {
        **BASE,
        "production": "icon-new",
        "frozen": False,
        "freeze_decision": {
            "type": "unfreeze",
            "reason": "ready",
            "approved_by": "maintainer",
            "approved_at": "2026-11-19T10:00:00Z",
        },
    }
    report = evaluate_freeze_policy(BASE, candidate, NOW)
    assert report["status"] == "fail"
    assert any("rollback_verified" in item for item in report["errors"])


def test_expiry_monitor_emits_7d_3d_24h_and_expired_alerts() -> None:
    pointers = {**BASE, "frozen": True}
    cases = [
        ("2026-11-17T12:00:00+00:00", "7d"),
        ("2026-11-13T12:00:00+00:00", "3d"),
        ("2026-11-11T12:00:00+00:00", "24h"),
        ("2026-11-09T12:00:00+00:00", "expired"),
    ]
    for expires_at, expected in cases:
        report = freeze_alert({**pointers, "freeze_expires_at": expires_at}, NOW)
        assert report["alert"] == expected


def test_expiry_monitor_skips_when_unfrozen() -> None:
    report = freeze_alert({**BASE, "frozen": False}, NOW)
    assert report["alert"] == "none"


def test_publish_gate_blocks_when_freeze_is_active() -> None:
    from scripts.freeze_policy_gate import evaluate_publish_policy

    report = evaluate_publish_policy(BASE, NOW)
    assert report["status"] == "fail"
    assert any("still active" in item for item in report["errors"])


def test_publish_gate_allows_after_explicit_unfreeze() -> None:
    from scripts.freeze_policy_gate import evaluate_publish_policy

    report = evaluate_publish_policy({**BASE, "frozen": False}, NOW)
    assert report["status"] == "pass"
