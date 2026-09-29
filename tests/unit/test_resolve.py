from popular_rules_icon.resolve import variant_url

def test_variant_url():
    m = {
        "entries": [
            {
                "service_id": "github",
                "variants": {
                    "source_original:256:png": {
                        "variant_hash": "abc123",
                        "path": "/v/abc123.png",
                    }
                },
            }
        ]
    }
    u = variant_url(m, "github")
    assert u and "abc123" in u
    assert variant_url(m, "missing") is None
