#!/usr/bin/env python3
"""R19 — HEAD-check sample CDN URLs from url map."""
from __future__ import annotations
import argparse, json, urllib.request
from pathlib import Path

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--url-map', type=Path, required=True)
    ap.add_argument('--sample', type=int, default=20)
    args=ap.parse_args()
    m=json.loads(args.url_map.read_text())
    items=list(m.items())[:args.sample]
    ok=fail=0
    for sid,url in items:
        try:
            req=urllib.request.Request(url, method='HEAD', headers={'User-Agent':'IconHealth/1.0'})
            with urllib.request.urlopen(req, timeout=15) as r:
                if r.status>=400: raise RuntimeError(r.status)
            ok+=1
        except Exception as e:
            fail+=1
            print('FAIL', sid, e)
    print(json.dumps({'checked':len(items),'ok':ok,'fail':fail}))
    return 0 if fail==0 else 1
if __name__=='__main__':
    raise SystemExit(main())
