#!/usr/bin/env bash
python3 - <<'PY'
import connectors as C
C.KEYWORDS[:] = ["designer"]
for j in C.sa_gov(): print("DESC", j["description"][:2500]); break
PY
