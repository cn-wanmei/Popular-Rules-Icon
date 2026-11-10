from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

from scripts.release_pointer_closure_gate import audit_release_pointers, EXPECTED_VARIANTS


def _fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    dist = tmp_path / "dist"
    (dist / "manifests").mkdir(parents=True)
    (dist / "v").mkdir()
    services = {"alpha": {}, "beta": {}}
    snapshot = tmp_path / "snapshot.json"
    snapshot.write_text(json.dumps({"services": services}), encoding="utf-8")
    pointers = tmp_path / "pointers.yaml"
    pointers.write_text(yaml.safe_dump({"production": "release-prod", "rollback": "release-rb"}), encoding="utf-8")
    for release_id in ("release-prod", "release-rb"):
        entries = []
        for service_id in services:
            variants = {}
            for key in sorted(EXPECTED_VARIANTS):
                variant_hash = hashlib.sha256(f"{release_id}:{service_id}:{key}".encode()).hexdigest()
                path = f"/v/{variant_hash}.png"
                (dist / path.lstrip("/")).write_bytes(b"png")
                variants[key] = {"variant_hash": variant_hash, "path": path, "key": key}
            entries.append({"service_id": service_id, "status": "active", "variants": variants})
        manifest = {
            "release_id": release_id, "content_hash": "a" * 64,
            "coverage_real": 1, "coverage_placeholder": 0, "entries": entries,
        }
        (dist / "manifests" / f"{release_id}.json").write_text(json.dumps(manifest), encoding="utf-8")
    return pointers, snapshot, dist


def test_release_pointer_gate_passes_for_complete_production_and_rollback(tmp_path: Path) -> None:
    pointers, snapshot, dist = _fixture(tmp_path)
    report = audit_release_pointers(pointers, snapshot, dist)
    assert report["status"] == "pass"
    assert [item["status"] for item in report["releases"]] == ["pass", "pass"]
    assert all(item["variant_records"] == 32 for item in report["releases"])


def test_release_pointer_gate_fails_when_a_rollback_variant_is_missing(tmp_path: Path) -> None:
    pointers, snapshot, dist = _fixture(tmp_path)
    rollback_path = dist / "manifests" / "release-rb.json"
    rollback = json.loads(rollback_path.read_text())
    missing = rollback["entries"][0]["variants"][sorted(EXPECTED_VARIANTS)[0]]["path"]
    (dist / missing.lstrip("/")).unlink()
    rollback_path.write_text(json.dumps(rollback), encoding="utf-8")
    report = audit_release_pointers(pointers, snapshot, dist)
    assert report["status"] == "fail"
    assert report["releases"][1]["missing_variant_files"] == 1


def test_release_pointer_gate_fails_for_missing_rollback_manifest(tmp_path: Path) -> None:
    pointers, snapshot, dist = _fixture(tmp_path)
    (dist / "manifests" / "release-rb.json").unlink()
    report = audit_release_pointers(pointers, snapshot, dist)
    assert report["status"] == "fail"
    assert report["releases"][1]["status"] == "fail"
