#!/usr/bin/env bash
mkdir -p discovery/out/h
python3 - <<'PY'
import os, time, fetch_logos as F
os.makedirs(F.OUT, exist_ok=True)
for n, d in [("HCF","hcf.com.au"),("NHVR","nhvr.gov.au")]:
    for i in range(3):
        r = F.one((n, d)); print("RESULT", n, r)
        if r[1]: break
        time.sleep(20)
PY
cp logos/hcf.com.au.* logos/nhvr.gov.au.* discovery/out/h/ 2>/dev/null; ls discovery/out/h
