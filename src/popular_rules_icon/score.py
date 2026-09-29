from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ScoreResult:
    total: int
    source_score: int
    quality_score: int
    source_class: str


def score_candidate(
    source_class: str,
    *,
    is_vector: bool,
    native_px: int,
    needs_upscale: bool,
    rules: dict[str, Any],
) -> ScoreResult:
    sp = rules.get("source_priority") or {}
    q = rules.get("quality") or {}
    source_score = int(sp.get(source_class, sp.get("placeholder", 0)))
    quality_score = 0
    if is_vector:
        quality_score += int(q.get("vector", 0))
    if native_px >= 512:
        quality_score += int(q.get("native_512", 0))
    elif native_px >= 256:
        quality_score += int(q.get("native_256", 0))
    if needs_upscale:
        quality_score += int(q.get("upscaled", 0))
    if native_px <= 0 and not is_vector:
        quality_score += int(q.get("unknown", 0))
    return ScoreResult(
        total=source_score + quality_score,
        source_score=source_score,
        quality_score=quality_score,
        source_class=source_class,
    )


def is_locked(lock: str | None) -> bool:
    return lock in {"service", "binding", "variant"}
