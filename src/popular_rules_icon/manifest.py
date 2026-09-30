from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from . import POLICY_VERSION, RENDERER_VERSION, SCHEMA_VERSION
from .hashutil import content_hash
from .pipeline import BuildResult


def build_physical_manifest(
    release_id: str,
    results: list[BuildResult],
    *,
    policy_snapshot: str | None = None,
) -> dict[str, Any]:
    entries = []
    real = 0
    placeholder = 0
    for r in results:
        if r.status == "placeholder":
            placeholder += 1
        elif r.status == "active" and r.object_hash:
            real += 1
        entries.append(
            {
                "service_id": r.service_id,
                "object_hash": r.object_hash,
                "variants": {
                    k: {"variant_hash": v, "path": f"/v/{v}.png", "key": k}
                    for k, v in sorted(r.variant_hashes.items())
                },
                "status": r.status,
                "source_class": r.source_class,
                "failure_code": r.failure_code,
            }
        )
    bindings = {
        r.service_id: {
            "object_hash": r.object_hash,
            "variant_hashes": r.variant_hashes,
            "status": r.status,
        }
        for r in results
    }
    ch = content_hash(
        bindings,
        schema_version=SCHEMA_VERSION,
        renderer_version=RENDERER_VERSION,
        policy_version=POLICY_VERSION,
        canon_version="1",
    )
    total = max(len(results), 1)
    return {
        "schema_version": SCHEMA_VERSION,
        "release_id": release_id,
        "content_hash": ch,
        "policy_snapshot": policy_snapshot,
        "renderer_version": RENDERER_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "coverage_real": real / total,
        "coverage_placeholder": placeholder / total,
        "entries": entries,
    }


def write_manifest(path: str, manifest: dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
