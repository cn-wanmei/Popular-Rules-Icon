import json

from scripts.icon_visual_identity_gate import audit, duplicate_group_authorized


def manifest_for(ids):
    keys = {
        f"{style}:{size}:png"
        for style in (
            "source_original",
            "glassmorphism",
            "soft_3d",
            "neo_skeuomorphism",
            "minimalist",
            "duotone_line",
            "mbe",
            "y2k",
        )
        for size in (128, 256)
    }
    return {
        "release_id": "test",
        "generated_at": "2026-10-06T00:00:00Z",
        "entries": [
            {
                "service_id": sid,
                "object_hash": "a" * 64,
                "source_class": "frozen_seed",
                "variants": {
                    key: {"variant_hash": "b" * 64, "path": f"/v/{'b' * 64}.png"}
                    for key in keys
                },
            }
            for sid in ids
        ],
    }


def test_alias_group_is_authorized():
    registry = {
        "root": {"service_id": "root"},
        "alias": {"service_id": "alias", "icon_alias_of": "root"},
    }
    assert duplicate_group_authorized(["root", "alias"], registry)


def test_multiple_unaliased_services_are_not_authorized():
    registry = {
        "one": {"service_id": "one"},
        "two": {"service_id": "two"},
    }
    assert not duplicate_group_authorized(["one", "two"], registry)


def test_external_alias_root_is_allowed():
    registry = {
        "alias_a": {"service_id": "alias_a", "icon_alias_of": "canonical"},
        "alias_b": {"service_id": "alias_b", "icon_alias_of": "canonical"},
    }
    assert duplicate_group_authorized(["alias_a", "alias_b"], registry)


def test_audit_flags_unauthorized_duplicate():
    report = audit(manifest_for(["one", "two"]), {
        "one": {"service_id": "one"},
        "two": {"service_id": "two"},
    })
    assert report["status"] == "drift"
    assert report["unauthorized_duplicate_object_groups"] == 1
