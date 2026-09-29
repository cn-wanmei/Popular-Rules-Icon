from __future__ import annotations

from pathlib import Path

from popular_rules_icon.pipeline import bindings_content_hash, process_svg_fixture
from popular_rules_icon.sanitize import SanitizeError, sanitize_svg

FIX = Path(__file__).resolve().parents[1] / "fixtures"


def test_sanitize_ok():
    data = (FIX / "geom_blue.svg").read_bytes()
    out = sanitize_svg(data)
    assert b"<svg" in out or b"svg" in out


def test_sanitize_blocks_script():
    data = (FIX / "geom_unsafe.svg").read_bytes()
    try:
        sanitize_svg(data)
        assert False, "expected SanitizeError"
    except SanitizeError as exc:
        assert exc.code == "SVG_UNSAFE"


def test_process_and_content_hash_stable():
    data = (FIX / "geom_blue.svg").read_bytes()
    r1 = process_svg_fixture("demo", data)
    r2 = process_svg_fixture("demo", data)
    assert r1.object_hash == r2.object_hash
    assert r1.variant_hashes == r2.variant_hashes
    h1 = bindings_content_hash([r1])
    h2 = bindings_content_hash([r2])
    assert h1 == h2
    assert r1.failure_code is None
    assert r1.status == "active"


def test_unsafe_fixture_failure_code():
    data = (FIX / "geom_unsafe.svg").read_bytes()
    r = process_svg_fixture("bad", data)
    assert r.failure_code == "SVG_UNSAFE"
