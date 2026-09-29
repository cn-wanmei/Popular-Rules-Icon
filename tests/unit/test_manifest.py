from popular_rules_icon.manifest import build_physical_manifest
from popular_rules_icon.pipeline import process_svg_fixture
from pathlib import Path

FIX = Path(__file__).resolve().parents[1] / "fixtures"

def test_physical_manifest():
    data = (FIX / "geom_blue.svg").read_bytes()
    r = process_svg_fixture("demo", data)
    m = build_physical_manifest("icon-2026.09.29.1", [r], policy_snapshot="sha256:dead")
    assert m["release_id"] == "icon-2026.09.29.1"
    assert m["content_hash"]
    assert m["entries"][0]["variants"]
