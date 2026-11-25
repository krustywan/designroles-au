#!/usr/bin/env bash
pip -q install pillow cairosvg
mkdir -p discovery/out/c
for e in png svg jpg ico; do curl -s -f "https://krustywan.github.io/designroles-au/logos/cottonon.com.$e" -o discovery/out/c/live.$e && echo "LIVE $e"; done
python3 - <<'PY'
import os, fetch_logos as F
os.makedirs(F.OUT, exist_ok=True)
print("RESULT", F.one(("Cotton On", "cottonon.com")))
PY
cp logos/cottonon.com.* discovery/out/c/ 2>/dev/null
python3 discovery/logo_probe.py 2>&1 | grep -E "CAND|ERR" | cut -c1-200
