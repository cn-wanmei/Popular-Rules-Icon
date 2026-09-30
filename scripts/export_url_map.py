#!/usr/bin/env python3
"""R18 — Export service_id → preferred CDN URL map from state (for Collection materialize)."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--state', type=Path, required=True)
    ap.add_argument('--style', default='source_original')
    ap.add_argument('--size', type=int, default=256)
    ap.add_argument('--out', type=Path, required=True)
    args=ap.parse_args()
    key=f'{args.style}:{args.size}:png'
    m={}
    for p in args.state.glob('*.json'):
        d=json.loads(p.read_text())
        vh=(d.get('variant_hashes') or {}).get(key)
        if vh:
            m[d['service_id']]=f'https://cdn.jsdelivr.net/gh/cn-wanmei/Popular-Rules-Icon@dist/v/{vh}.png'
    args.out.write_text(json.dumps(m, ensure_ascii=False, indent=2)+'\n')
    print('exported', len(m), '->', args.out)
    return 0
if __name__=='__main__':
    raise SystemExit(main())
