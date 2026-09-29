from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pipeline import bindings_content_hash, process_svg_fixture
from .schema_load import list_schemas


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="pri-icon")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("schemas", help="list schema files")
    s.set_defaults(func=cmd_schemas)

    s = sub.add_parser("fixture-run", help="L1: process fixture SVG → content_hash")
    s.add_argument("--svg", required=True)
    s.add_argument("--service-id", default="demo")
    s.set_defaults(func=cmd_fixture_run)

    s = sub.add_parser("validate-registry", help="basic registry JSON presence check")
    s.add_argument("--dir", default="registry/services")
    s.set_defaults(func=cmd_validate_registry)

    args = p.parse_args(argv)
    return int(args.func(args))


def cmd_schemas(_args: argparse.Namespace) -> int:
    print(json.dumps(list_schemas(), indent=2))
    return 0


def cmd_fixture_run(args: argparse.Namespace) -> int:
    data = Path(args.svg).read_bytes()
    r = process_svg_fixture(args.service_id, data)
    out = {
        "service_id": r.service_id,
        "object_hash": r.object_hash,
        "variant_hashes": r.variant_hashes,
        "status": r.status,
        "failure_code": r.failure_code,
        "content_hash": bindings_content_hash([r]) if r.object_hash else None,
    }
    print(json.dumps(out, indent=2))
    return 0 if r.failure_code is None else 1


def cmd_validate_registry(args: argparse.Namespace) -> int:
    d = Path(args.dir)
    files = sorted(d.glob("*.json"))
    if not files:
        print("no registry files")
        return 1
    for f in files:
        json.loads(f.read_text(encoding="utf-8"))
    print(json.dumps({"count": len(files), "ok": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
