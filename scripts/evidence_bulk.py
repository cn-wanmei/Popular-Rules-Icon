#!/usr/bin/env python3
"""R17 — Generate evidence/<sid>/source.json from seed + registry."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from datetime import datetime, timezone

def main() -> int:
    seed=Path('assets/icons/seed')
    reg=Path('registry/services')
    root=Path('evidence')
    n=0
    for p in reg.glob('*.json'):
        sid=p.stem
        d=json.loads(p.read_text())
        seeds=list(seed.glob(f'{sid}.*'))
        if not seeds: continue
        data=seeds[0].read_bytes()
        sha=hashlib.sha256(data).hexdigest()
        out=root/sid
        out.mkdir(parents=True, exist_ok=True)
        (out/'source.json').write_text(json.dumps({
            'service_id': sid,
            'source_url': f'seed://{seeds[0].name}',
            'retrieved_at': datetime.now(timezone.utc).isoformat(),
            'source_class': d.get('notes','') and 'frozen_seed' or 'frozen_seed',
            'sha256': sha,
            'review_status': d.get('review_status') or d.get('notes'),
            'usage_basis': 'identifier_use_takedown',
        }, ensure_ascii=False, indent=2)+'\n')
        n+=1
    print(f'evidence packs: {n}')
    return 0
if __name__=='__main__':
    raise SystemExit(main())
