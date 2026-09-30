#!/usr/bin/env python3
import json, sys
from pathlib import Path
REQUIRED = {
  f"{s}:{sz}:png"
  for s in ("source_original","glassmorphism","soft_3d","neo_skeuomorphism","minimalist","duotone_line","mbe","y2k")
  for sz in (128, 256)
}
def main(state_dir: Path) -> int:
    fails=[]
    for p in sorted(state_dir.glob("*.json")):
        d=json.loads(p.read_text())
        keys=set((d.get("variant_hashes") or {}).keys())
        miss=REQUIRED-keys
        if miss:
            fails.append((p.stem, sorted(miss)[:4]))
    if fails:
        print("STYLES GATE FAIL", len(fails))
        for s,m in fails[:20]:
            print(s, m)
        return 1
    print("STYLES GATE PASS", len(list(state_dir.glob('*.json'))))
    return 0
if __name__=='__main__':
    raise SystemExit(main(Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/s8-state')))
