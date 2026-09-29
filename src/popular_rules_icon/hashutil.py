from __future__ import annotations

import hashlib
import json
from typing import Any


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def object_hash(canonical_bytes: bytes) -> str:
    return sha256_bytes(canonical_bytes)


def variant_hash(
    obj_hash: str,
    *,
    renderer_version: str,
    style: str,
    size: int,
    fmt: str,
    policy_version: str,
) -> str:
    payload = f"{obj_hash}|{renderer_version}|{style}|{size}|{fmt}|{policy_version}"
    return sha256_text(payload)


def content_hash(
    bindings: dict[str, dict[str, Any]],
    *,
    schema_version: str,
    renderer_version: str,
    policy_version: str,
    canon_version: str,
) -> str:
    """Deterministic hash over normalized bindings; excludes timestamps/URLs."""
    normalized: dict[str, Any] = {}
    for sid in sorted(bindings.keys()):
        b = bindings[sid]
        normalized[sid] = {
            "object_hash": b.get("object_hash"),
            "variant_hashes": {
                k: b["variant_hashes"][k]
                for k in sorted((b.get("variant_hashes") or {}).keys())
            },
            "status": b.get("status"),
        }
    blob = json.dumps(
        {
            "bindings": normalized,
            "schema_version": schema_version,
            "renderer_version": renderer_version,
            "policy_version": policy_version,
            "canon_version": canon_version,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256_text(blob)


def source_fingerprint(
    url: str,
    etag: str | None,
    last_modified: str | None,
    content_length: int | None,
) -> str:
    payload = f"{url}|{etag or ''}|{last_modified or ''}|{content_length if content_length is not None else ''}"
    return sha256_text(payload)
