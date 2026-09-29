from __future__ import annotations

import json
from pathlib import Path

from popular_rules_icon.schema_load import list_schemas, load_schema

ROOT = Path(__file__).resolve().parents[2]


def test_all_schemas_load():
    names = list_schemas()
    assert names
    for n in names:
        data = load_schema(n)
        assert isinstance(data, dict)
        assert "$schema" in data or "type" in data


def test_registry_sample_shape():
    sample = {
        "service_id": "github",
        "name": "GitHub",
        "domains": ["github.com"],
        "aliases": ["gh"],
        "renamed_from": [],
        "asset_class": "brand",
        "tier": 0,
        "status": "active",
        "lock": "none",
    }
    schema = load_schema("registry.schema.json")
    assert schema["required"] == ["service_id", "name", "status"]
    for key in schema["required"]:
        assert key in sample
