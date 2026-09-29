from popular_rules_icon.score import is_locked, score_candidate

RULES = {
    "source_priority": {
        "manual_review": 1000,
        "official_svg": 800,
        "low_res_favicon": 100,
        "placeholder": 0,
    },
    "quality": {"vector": 200, "native_256": 100, "upscaled": -300},
}


def test_manual_beats_favicon():
    a = score_candidate("manual_review", is_vector=True, native_px=256, needs_upscale=False, rules=RULES)
    b = score_candidate("low_res_favicon", is_vector=False, native_px=32, needs_upscale=True, rules=RULES)
    assert a.total > b.total


def test_lock_helper():
    assert is_locked("service")
    assert not is_locked("none")
    assert not is_locked(None)
