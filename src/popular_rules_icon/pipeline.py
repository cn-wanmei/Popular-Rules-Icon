from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from . import CANON_VERSION, POLICY_VERSION, RENDERER_VERSION, SCHEMA_VERSION
from .hashutil import content_hash, object_hash, variant_hash
from .sanitize import SanitizeError, sanitize_svg
from .score import is_locked, score_candidate


@dataclass
class BuildResult:
    service_id: str
    object_hash: str | None = None
    variant_hashes: dict[str, str] = field(default_factory=dict)
    status: str = "active"
    source_class: str | None = None
    failure_code: str | None = None
    score_total: int | None = None


def process_svg_fixture(
    service_id: str,
    svg_bytes: bytes,
    *,
    source_class: str = "manual_review",
    styles: list[str] | None = None,
    sizes: list[int] | None = None,
    lock: str = "none",
    rules: dict[str, Any] | None = None,
) -> BuildResult:
    """Deterministic path used by L1 fixtures (no network)."""
    styles = styles or ["source_original"]
    sizes = sizes or [256]
    rules = rules or {
        "source_priority": {"manual_review": 1000, "placeholder": 0},
        "quality": {"vector": 200, "native_256": 100, "upscaled": -300},
    }
    try:
        clean = sanitize_svg(svg_bytes)
    except SanitizeError as exc:
        return BuildResult(service_id=service_id, status="gone", failure_code=exc.code)

    oh = object_hash(clean)
    sc = score_candidate(
        source_class,
        is_vector=True,
        native_px=256,
        needs_upscale=False,
        rules=rules,
    )
    variants: dict[str, str] = {}
    for style in styles:
        for size in sizes:
            # source_original only for fixtures; decorative styles deferred
            key = f"{style}:{size}:png"
            variants[key] = variant_hash(
                oh,
                renderer_version=RENDERER_VERSION,
                style=style,
                size=size,
                fmt="png",
                policy_version=POLICY_VERSION,
            )
    status = "active"
    if is_locked(lock):
        # locked still produces output; auto-replace forbidden elsewhere
        pass
    return BuildResult(
        service_id=service_id,
        object_hash=oh,
        variant_hashes=variants,
        status=status,
        source_class=source_class,
        score_total=sc.total,
    )


def bindings_content_hash(results: list[BuildResult]) -> str:
    bindings = {
        r.service_id: {
            "object_hash": r.object_hash,
            "variant_hashes": r.variant_hashes,
            "status": r.status,
        }
        for r in results
    }
    return content_hash(
        bindings,
        schema_version=SCHEMA_VERSION,
        renderer_version=RENDERER_VERSION,
        policy_version=POLICY_VERSION,
        canon_version=CANON_VERSION,
    )
