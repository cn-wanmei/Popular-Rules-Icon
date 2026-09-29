from __future__ import annotations

import argparse
import json
from pathlib import Path

from .canary import acquire_canary
from .manifest import build_physical_manifest, write_manifest
from .pipeline import bindings_content_hash, process_svg_fixture
from .schema_load import list_schemas


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="pri-icon")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("schemas", help="list schema files")
    s.set_defaults(func=cmd_schemas)

    s = sub.add_parser("fixture-run", help="L1: process fixture SVG")
    s.add_argument("--svg", required=True)
    s.add_argument("--service-id", default="demo")
    s.set_defaults(func=cmd_fixture_run)

    s = sub.add_parser("validate-registry", help="registry JSON presence")
    s.add_argument("--dir", default="registry/services")
    s.set_defaults(func=cmd_validate_registry)

    s = sub.add_parser("acquire-canary", help="R1: fetch official sources into state JSON")
    s.add_argument("--official-sources", default="config/official_sources.yaml")
    s.add_argument("--services", required=True, help="comma-separated service ids")
    s.add_argument("--out-state", required=True)
    s.add_argument("--out-objects", default="")
    s.set_defaults(func=cmd_acquire_canary)

    s = sub.add_parser("build-manifest", help="R3: physical manifest from state dir")
    s.add_argument("--state-dir", required=True)
    s.add_argument("--release-id", required=True)
    s.add_argument("--out", required=True)
    s.set_defaults(func=cmd_build_manifest)

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


def cmd_acquire_canary(args: argparse.Namespace) -> int:
    ids = [x.strip() for x in args.services.split(",") if x.strip()]
    summary = acquire_canary(
        official_sources=Path(args.official_sources),
        service_ids=ids,
        out_state=Path(args.out_state),
        out_objects=Path(args.out_objects) if args.out_objects else None,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if not summary.get("failed") else 1


def cmd_build_manifest(args: argparse.Namespace) -> int:
    from .pipeline import BuildResult

    results = []
    for f in sorted(Path(args.state_dir).glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        results.append(
            BuildResult(
                service_id=d["service_id"],
                object_hash=d.get("object_hash"),
                variant_hashes=d.get("variant_hashes") or {},
                status="active" if d.get("object_hash") else "orphaned",
                source_class=d.get("source_class"),
                failure_code=d.get("last_failure_code"),
            )
        )
    m = build_physical_manifest(args.release_id, results, policy_snapshot="policies/render-policy-v1.yaml")
    write_manifest(args.out, m)
    print(json.dumps({"release_id": m["release_id"], "content_hash": m["content_hash"], "entries": len(m["entries"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
